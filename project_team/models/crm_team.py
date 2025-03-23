# See LICENSE file for full copyright and licensing details.
import logging
import ast
from odoo import fields, models, api


class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'

    type_team = fields.Selection([('sale', 'Sale'), ('project', 'Project')], ('helpdesk', 'Helpdesk')],
                                 string="Team Type", default="sale")
    team_members_ids = fields.Many2many('res.users', 'project_team_user_rel',
                                        'team_id', 'user_id', 'Project Members',
                                        help="""Project's members are users who
                                     can have an access to the tasks related
                                     to this project.""")

class ProductAtributesUserInherit(models.Model):
    _inherit = 'res.users'

    member_atributes_ids = fields.Many2many(
        'product.attribute.value',  # Model představující hodnoty tů
        'product_attributes_user_rel',  # Jméno relační tabulky
        'user_id',  # Jméno sloupce odkazujícího na `res.users`
        'attribute_value_id',  # Jméno sloupce odkazujícího na `product.attribute.value`
        string='Attributes'
    )
class IrModule(models.Model):
    _inherit = "ir.module.module"

    def remove_action(self, action_data):
        domain_lst = ast.literal_eval(action_data.domain)
        return [domain for domain in domain_lst if domain[0] != 'type_team']
    
    def module_uninstall(self):
        action_references = [
            'sales_team.crm_team_action_sales',
            'sales_team.crm_team_action_config'
        ]
        
        for ref in action_references:
            action_data = self.env.ref(ref)
            if action_data and action_data.domain:
                action_data.write({'domain': self.remove_action(action_data)})
    
        return super().module_uninstall()
        

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.onchange('team_id')
    def _onchange_team_id(self):
        """Při změně projektového týmu se aktualizují odpovědné osoby ve všech úkolech projektu."""
        if self.team_id:
            _logger.info("Změna týmu projektu na: %s (ID: %s)", self.team_id.name, self.team_id.id)
            
            # Získáme všechny úkoly tohoto projektu
            tasks = self.env['project.task'].search([('project_id', '=', self._origin.id)])
            _logger.info("Nalezeno %s úkolů pro projekt ID %s.", len(tasks), self._origin.id)
            
            for task in tasks:
                # Získání produktu z sale_line_id
                product = task.sale_line_id.product_id
                if not product:
                    _logger.warning("Úkol ID %s nemá přiřazený produkt přes sale_line_id.", task.id)
                    continue
                _logger.info("Úkol ID %s má přiřazený produkt: %s (ID: %s)", task.id, product.name, product.id)
                
                # Kontrola produktových atributů varianty produktu
                product_attributes = product.product_template_variant_value_ids
                if not product_attributes:
                    _logger.warning("Produkt ID %s nemá přiřazené atributy (product_template_attribute_value_ids).", product.id)
                    continue
                _logger.info("Produkt ID %s má %s atributů.", product.id, len(product_attributes))
                
                # Výpis všech atributů produktu pro podrobné logování
                for attribute in product_attributes:
                    _logger.info("Produkt ID %s - Atribut: %s (ID: %s)", product.id, attribute.name, attribute.id)
                
                # Mapped list of attribute names for comparison
                product_attribute_names = product_attributes.mapped('name')
                _logger.info("Seznam názvů atributů produktu ID %s: %s", product.id, product_attribute_names)
                
                # Výběr členů týmu s odpovídajícími názvy atributů
                matching_users = self.env['res.users'].search([
                    ('id', 'in', self.team_id.team_members_ids.ids),
                    ('member_atributes_ids.name', 'in', product_attribute_names)
                ])
                
                if matching_users:
                    task.user_ids = [(6, 0, matching_users.ids)]
                    _logger.info("Přiřazeni odpovědní uživatelé k úkolu ID %s: %s", task.id, matching_users.mapped('name'))
                    for user in matching_users:
                        _logger.info("Člen týmu přiřazen k úkolu ID %s - Jméno: %s (ID: %s)", task.id, user.name, user.id)
                        for user_attr in user.member_atributes_ids:
                            _logger.info("Atribut člena týmu: %s (ID: %s)", user_attr.name, user_attr.id)
                else:
                    _logger.warning(
                        "Pro úkol ID %s nebyli nalezeni žádní členové týmu s odpovídajícími atributy. "
                        "Tým ID: %s, Produkt ID: %s, Počet atributů produktu: %s, Členové týmu ID: %s",
                        task.id, self.team_id.id, product.id, len(product_attributes), self.team_id.team_members_ids.ids
                    )
                    for user in self.team_id.team_members_ids:
                        _logger.info("Člen týmu %s (ID: %s), Atributy uživatele:", user.name, user.id)
                        for user_attr in user.member_atributes_ids:
                            _logger.info("Atribut uživatele: %s (ID: %s)", user_attr.name, user_attr.id)


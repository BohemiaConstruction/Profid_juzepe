###################################################################################
#
#    Copyright 2024 Systee s.r.o. (<https://www.systee.cz>)
#
#    Systee Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used
#    if you have purchased a valid license from Systee s.r.o.
#
#    The above permissions are granted for a single database per purchased
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using
#    its resources), but without copying any source code or material from
#    the Software.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
#
###################################################################################

{
    'name': 'Product forecast based on sale history',
    'version': '17.0.0.0.1',
    'summary': "Forecast Sale History",
    'author': 'Systee s.r.o. (https://www.systee.cz)',
    'license': 'Other proprietary',
    'category': 'Stock',
    'depends': ['sale', 'stock'],
    'external_dependencies': {'python': ['numpy']},
    'data': [
        'views/product_template_view.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
}
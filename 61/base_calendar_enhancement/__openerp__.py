# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2012 Noviat nv/sa (www.noviat.be). All rights reserved.
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'base calendar fix',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category' : 'Generic Modules',
    'description': """
    
    Fix the fact you can't filter by date or something else on the tree view.

    This is just a pack of function took from the trunk version (2014/06/24) which replace the ways it work on the search function. 
        
    """,
    'depends': ['base_calendar'],
    'demo_xml': [],
    'init_xml': [],
    'update_xml' : [],
    'auto_install': False,
    }

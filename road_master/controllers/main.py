# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import base64
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import AccessError, MissingError

class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        domain = []
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        if request.env.user.sudo().has_group('base.group_portal'):
             domain += [('user_id', '=', request.env.user.id)]
        installation_count = request.env['device.installation'].sudo().search_count(domain)
        values['installation_count'] = installation_count
        return values

    def _devise_installation_get_page_view_values(self, installation, access_token, **kwargs):
        values = {
            'page_name': 'Devise Installations',
            'installation': installation,
        }
        return self._get_page_view_values(installation, access_token, values, False, False, **kwargs)

    @http.route(['/my/installation/<int:installation_id>'], type='http', auth="public", website=True)
    def portal_my_installation(self, installation_id=None, access_token=None, report_type=None, download=True, **kw):
        installation = request.env['device.installation'].sudo()
        redirect = ("/my/installation")
        try:
            insllation_sudo = installation_id and installation.browse(installation_id) or False
            values = insllation_sudo
        except Exception as e:
            return request.redirect("%s?error_msg=%s" % (redirect, (e)))
        post = values
        return request.render("road_master.installation_portal_content", {'post': post})

    @http.route(['/my/installation', '/my/installation/page/<int:page>'], type='http', auth="public", website=True)
    def portal_my_installation_details(self, page=1, search=None, **kw):
        installation_sudo = request.env['device.installation'].sudo()
        domain = []
        if request.env.user.sudo().has_group('base.group_portal'):
            domain += [('user_id', '=', request.env.user.id)]
        installation = installation_sudo.sudo().search(domain)
        grouped_installation = [installation]

        values = {
            'installation': installation,
            'page_name': 'Devise Installation',
            'grouped_installation': installation,
            'default_url': '/my/installation',
            'currency': request.env.user.company_id.currency_id,
        }
        return request.render("road_master.portal_my_installations", values)

    @http.route(['/my/signature/<int:inslattion_id>'], type='json', auth="public", website=True)
    def save_installation_signature(self, inslattion_id=None, **kw):
        try:
            installation = request.env['device.installation'].sudo()
            installation_sudo = inslattion_id and installation.browse(inslattion_id) or False
            attachment_value = {
                'name': 'Installment Signature',
                'datas': kw.get('signature'),
                'res_model': 'device.installation',
                'res_id': installation_sudo.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            if attachment_id:
                installation_sudo.is_sign = True
                installation_sudo.action_done()
        except (AccessError, MissingError):
            return {'error': _('Invalid installation.')}
        return {
            'force_refresh': True,
            'redirect_url': '/my/installation/%s'%inslattion_id,
        }

# -*- coding: utf-8 -*-

from odoo import models,fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_rmts_device = fields.Boolean("RMTS Device", copy=False, help="Product is RMTS Device.")
    item_code = fields.Char("Item Code", copy=False, help="Device Item Code")
    hardware_type_id = fields.Many2one("hardware.type", string="Hardware Type")
    gsm_type = fields.Selection([("internal", "Internal"),
                                 ("external", "External")],
                                string="GSM Type",default="internal")
    network_type = fields.Selection([("ble", "BLE"),
                                     ("wifi", "WIFI"),
                                     ("3g", "3G"),
                                     ("4g", "4G"),
                                     ("5g", "5G")],
                                    string="Network Type", default="4g")
    gps = fields.Selection([("internal", "Internal"),
                            ("external", "External")],
                           string="GPS", default="internal")
    internal_battery = fields.Boolean("Internal Battery")
    digital_input = fields.Boolean("Digital Input")
    voice_monitoring = fields.Boolean("Voice Monitoring")
    digital_output = fields.Boolean("Digital Output")
    analog_input = fields.Boolean("Analog Input")
    wire = fields.Boolean("Wire")
    memory_card_slot = fields.Boolean("Memory Card Slot")
    operating_temperature = fields.Char("Operating Temperature")
    device_length = fields.Float("Length")
    device_width = fields.Float("Width")
    device_height = fields.Float("Height")
    device_uom_id = fields.Many2one("uom.uom", string="Unit of Measure", help="Unit of measure for dimensions.")
    device_description = fields.Text("Device Description")
    device_remarks = fields.Text("Remarks")
    product_image_ids = fields.One2many("product.image", "product_template_id", string="Images", copy=False, help="Product Images.")

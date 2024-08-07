import frappe
from frappe import _

no_cache = 1

@frappe.whitelist()
def update_or_create_address(customer_name, address_data):
    # Check if the address exists for the customer
    existing_address = frappe.get_all("Address",
                                      filters={"owner": customer_name, "is_primary_address": 1},
                                      fields=["name","owner"])

    if existing_address:
        existing_address_doc = frappe.get_doc("Address", existing_address[0]["name"])
        existing_address_doc.update(address_data)
        existing_address_doc.save()
        return {"message": _("Address updated successfully.")}
    else:
        # Address does not exist, create it
        address_doc = frappe.new_doc("Address")
        address_doc.update({
            "owner": customer_name,
            **address_data
        })
        address_doc.insert()
        return {"message": _("Address created successfully.")}



@frappe.whitelist(allow_guest=True)
def get_user_info():
    current_user = frappe.session.user

    # Fetch the associated customer
    customer_name = None
    if current_user and current_user != "Guest":
        customer_record = frappe.get_all("Customer", filters={"owner": current_user}, fields=["customer_name"])
        if customer_record:
            customer_name = customer_record[0].customer_name

    return {
        "current_user": current_user,
        "customer_name": customer_name
    }

@frappe.whitelist(allow_guest=True)
def get_csrf_token():
    return {
        "csrf_token": frappe.sessions.get_csrf_token()
    }
    

@frappe.whitelist(allow_guest=True)
def check_user_product_purchase(product_id):
    current_user = frappe.session.user

    if current_user and current_user != "Guest":
        user_products = frappe.get_all("User Products", filters={"user": current_user}, fields=["product"])
        owned_products = [product.product for product in user_products]

        if product_id in owned_products:
            return {"status": "error", "message": _("You already own this product.")}

    return {"status": "success", "message": _("You can purchase this product.")}

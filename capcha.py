from anticaptchaofficial.funcaptchaproxyless import *

solver = funcaptchaProxyless()
solver.set_verbose(1)
solver.set_key("69ad73e41bee9d0444294084e44a104d")
solver.set_website_url("https://accounts.snapchat.com/accounts/v2/signup")
solver.set_website_key("EA4B65CB-594A-438E-B4B5-D0DBA28C9334")

# optional funcaptcha API subdomain, see our Funcaptcha documentation for details
solver.set_js_api_domain("snap-api.arkoselabs.com")

# optional data[blob] value, read the docs
# solver.set_data_blob("{\"blob\":\"DATA_BLOB_VALUE_HERE\"}")

# Specify softId to earn 10% commission with your app.
# Get your softId here: https://anti-captcha.com/clients/tools/devcenter
solver.set_soft_id(0)

token = solver.solve_and_return_solution()
if token != 0:
    print("result token: "+token)
else:
    print("task finished with error "+solver.error_code)
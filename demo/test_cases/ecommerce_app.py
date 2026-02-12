"""
TEST CASE 2: E-commerce Platform
Vulnerabilities: XSS, Path Traversal, Insecure File Operations
"""

import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded secret keys
# FAKE TEST DATA - Not real credentials
SECRET_KEY = "my-super-secret-key-12345"  # gitleaks:allow
STRIPE_API_KEY = "sk_test_FAKE_STRIPE_KEY_FOR_DEMO"  # gitleaks:allow
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"  # gitleaks:allow
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # gitleaks:allow

@app.route('/product/<product_id>')
def show_product(product_id):
    """Display product details"""
    # VULNERABILITY 2: XSS vulnerability - unescaped user input
    html = f"<h1>Product Details</h1><p>Product ID: {product_id}</p>"
    return render_template_string(html)

@app.route('/search')
def search_products():
    """Search for products"""
    query = request.args.get('q', '')
    
    # VULNERABILITY 3: XSS in search results
    results_html = f"""
    <html>
        <body>
            <h2>Search Results for: {query}</h2>
            <p>Found {len(query)} results</p>
        </body>
    </html>
    """
    return render_template_string(results_html)

@app.route('/download')
def download_invoice():
    """Download customer invoice"""
    filename = request.args.get('file')
    
    # VULNERABILITY 4: Path Traversal - user controls file path
    file_path = "/var/invoices/" + filename
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except:
        return "File not found"

@app.route('/upload', methods=['POST'])
def upload_product_image():
    """Upload product images"""
    file = request.files['image']
    filename = request.form.get('filename')
    
    # VULNERABILITY 5: Path Traversal in upload
    upload_path = os.path.join('/var/uploads/', filename)
    file.save(upload_path)
    
    return f"File uploaded to {upload_path}"

@app.route('/user/profile')
def user_profile():
    """Display user profile"""
    user_id = request.args.get('id')
    username = request.args.get('name')
    
    # VULNERABILITY 6: XSS via innerHTML (if rendered in client)
    profile_html = f"""
    <div id="profile">
        <script>
            document.getElementById('profile').innerHTML = '{username}';
        </script>
    </div>
    """
    return profile_html

@app.route('/review/<product_id>')
def show_reviews(product_id):
    """Show product reviews"""
    review_text = request.args.get('review', '')
    
    # VULNERABILITY 7: XSS in user-generated content
    html = f"""
    <html>
        <body>
            <h3>Reviews for Product {product_id}</h3>
            <div class="review">{review_text}</div>
        </body>
    </html>
    """
    return render_template_string(html)

# VULNERABILITY 8: Debug mode enabled in production
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

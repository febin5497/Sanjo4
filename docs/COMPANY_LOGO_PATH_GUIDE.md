# Company Logo Path - Complete Guide (Web & Mobile)

## Backend Configuration

### Base URL Determination
```javascript
// api.js - Frontend auto-detects environment
const getBaseURL = () => {
    const host = window.location.hostname
    // If accessing via IP address (mobile on WiFi), use same IP
    if (host !== 'localhost' && host !== '127.0.0.1') {
        return `http://${host}:5000`
    }
    return "http://localhost:5000"
}
```

### Storage Paths

**Database Field**:
```
Table: companies
Column: logo_url
```

**Upload Directory**:
```
/uploads/logos/          (Main logo directory)
/uploads/logos/1/        (Company ID 1)
/uploads/logos/2/        (Company ID 2)
```

**Static Directory** (Alternative):
```
/static/                 (Static assets)
/static/logo.jpg         (Default company logo)
```

---

## Complete Logo Paths

### Path 1: Web Browser (Development)
```
Frontend: http://localhost:3000 (Vite dev server)
Backend: http://localhost:5000

Complete Logo Path:
http://localhost:5000/uploads/logos/{company_id}/logo.png

Example:
http://localhost:5000/uploads/logos/1/logo.png
```

### Path 2: Web Browser (Production)
```
Frontend: http://example.com (Your domain)
Backend: http://api.example.com or http://example.com/api

Complete Logo Path:
http://example.com/uploads/logos/{company_id}/logo.png

Example:
http://example.com/uploads/logos/1/logo.png
```

### Path 3: Mobile App (Same WiFi Network)
```
Frontend: Mobile App (React Native or Flutter)
Backend: http://{PC_IP_ADDRESS}:5000

Complete Logo Path:
http://{PC_IP_ADDRESS}:5000/uploads/logos/{company_id}/logo.png

Example:
http://192.168.1.100:5000/uploads/logos/1/logo.png
```

---

## Implementation Methods

### Method 1: Direct File Upload (Recommended)

**Frontend (Upload Logo)**:
```javascript
const handleLogoUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company_id', currentCompanyId)

    try {
        const response = await api.post('/api/company/upload-logo', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        const logoUrl = response.data.logo_url
        // Save to company settings
        await updateCompanyLogo(logoUrl)
    } catch (error) {
        console.error('Upload failed:', error)
    }
}
```

**Backend (Accept Upload)**:
```python
@app.route('/api/company/upload-logo', methods=['POST'])
@jwt_required()
def upload_logo():
    file = request.files.get('file')
    company_id = request.form.get('company_id')

    if not file:
        return error_response("No file provided", status_code=400)

    # Create directory if not exists
    upload_dir = f"uploads/logos/{company_id}"
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    filename = secure_filename("logo.png")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Save URL to database
    logo_url = f"/uploads/logos/{company_id}/logo.png"
    company = Company.query.get(company_id)
    company.logo_url = logo_url
    db.session.commit()

    return success_response({
        "logo_url": logo_url,
        "full_url": f"{request.host_url.rstrip('/')}{logo_url}"
    })
```

### Method 2: Store URL as Text (Simple)

**Frontend (Set Logo URL Manually)**:
```javascript
const updateCompanyLogo = async (logoUrl) => {
    await api.put('/api/company/settings', {
        logo_url: logoUrl
    })
}

// Usage
updateCompanyLogo("http://localhost:5000/static/logo.jpg")
updateCompanyLogo("/uploads/logos/1/logo.png")
```

**Backend (Already Implemented)**:
```python
# company_settings/routes.py
@company_settings_bp.route("", methods=["PUT"])
@jwt_required()
def update_company():
    data = request.get_json()
    company = Company.query.first()

    if "logo_url" in data:
        company.logo_url = data["logo_url"]  # Save the URL path

    db.session.commit()
    return success_response(company.to_dict())
```

---

## Frontend Usage (React)

### In Components

**Display Company Logo**:
```jsx
import { useEffect, useState } from 'react'
import api from '../api/api'

const CompanyLogo = () => {
    const [company, setCompany] = useState(null)

    useEffect(() => {
        const fetchCompany = async () => {
            try {
                const response = await api.get('/api/company/settings')
                setCompany(response.data.data)
            } catch (error) {
                console.error('Failed to fetch company:', error)
            }
        }
        fetchCompany()
    }, [])

    if (!company?.logo_url) {
        return <div>No logo</div>
    }

    // Build complete URL
    const logoUrl = company.logo_url.startsWith('http')
        ? company.logo_url
        : `${getBaseURL()}${company.logo_url}`

    return (
        <img
            src={logoUrl}
            alt="Company Logo"
            style={{ maxWidth: '150px', height: 'auto' }}
        />
    )
}

export default CompanyLogo
```

**In Invoice Template**:
```jsx
<div className="invoice-header">
    {company?.logo_url && (
        <img
            src={company.logo_url.startsWith('http')
                ? company.logo_url
                : `${getBaseURL()}${company.logo_url}`}
            alt="Company Logo"
            style={{ maxWidth: '100px' }}
        />
    )}
    <h1>{company?.name}</h1>
</div>
```

---

## Database Schema

### Companies Table
```sql
CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    logo_url VARCHAR(255),  -- Stores the path like: /uploads/logos/1/logo.png
    gst_number VARCHAR(50),
    tax_percentage FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Example Data
```sql
INSERT INTO companies (name, email, phone, logo_url, gst_number) VALUES
('ABC Construction', 'info@abc.com', '9876543210', '/uploads/logos/1/logo.png', '18AABCU1234H1Z0'),
('XYZ Builders', 'info@xyz.com', '9999999999', '/uploads/logos/2/logo.png', '27AABCX5678H2Z0');
```

---

## API Response Format

### Get Company Settings
```
GET /api/company/settings

Response:
{
    "success": true,
    "data": {
        "id": 1,
        "name": "ABC Construction",
        "email": "info@abc.com",
        "phone": "9876543210",
        "address": "123 Street, City",
        "logo_url": "/uploads/logos/1/logo.png",
        "gst_number": "18AABCU1234H1Z0",
        "tax_percentage": 18.0
    }
}
```

### Update Company Logo
```
PUT /api/company/settings

Request:
{
    "logo_url": "/uploads/logos/1/logo.png"
}

Response:
{
    "success": true,
    "data": {
        "logo_url": "/uploads/logos/1/logo.png"
    }
}
```

### Upload Logo Endpoint (To Be Created)
```
POST /api/company/upload-logo

Request:
FormData {
    file: <image_file>,
    company_id: 1
}

Response:
{
    "success": true,
    "data": {
        "logo_url": "/uploads/logos/1/logo.png",
        "full_url": "http://localhost:5000/uploads/logos/1/logo.png"
    }
}
```

---

## URL Construction Examples

### Web (Development)
```
Base URL: http://localhost:5000
Stored in DB: /uploads/logos/1/logo.png
Complete URL: http://localhost:5000/uploads/logos/1/logo.png
```

### Web (Production)
```
Base URL: https://example.com
Stored in DB: /uploads/logos/1/logo.png
Complete URL: https://example.com/uploads/logos/1/logo.png
```

### Mobile (Same WiFi)
```
Base URL: http://192.168.1.100:5000
Stored in DB: /uploads/logos/1/logo.png
Complete URL: http://192.168.1.100:5000/uploads/logos/1/logo.png
```

---

## Frontend Helper Function

```javascript
// utils/logoHelper.js

import { getBaseURL } from '../api/api'

export const getLogoUrl = (storedLogoUrl) => {
    if (!storedLogoUrl) {
        return null
    }

    // If already a complete URL, return as-is
    if (storedLogoUrl.startsWith('http://') || storedLogoUrl.startsWith('https://')) {
        return storedLogoUrl
    }

    // If relative path, prepend base URL
    return `${getBaseURL()}${storedLogoUrl}`
}

// Usage in components
import { getLogoUrl } from '../utils/logoHelper'

const logo = getLogoUrl(company.logo_url)
// Result: http://localhost:5000/uploads/logos/1/logo.png
```

---

## Summary

### Logo Path for WEB & MOBILE

| Environment | Complete URL |
|-------------|--------------|
| **Web (Dev)** | `http://localhost:5000/uploads/logos/{id}/logo.png` |
| **Web (Prod)** | `https://example.com/uploads/logos/{id}/logo.png` |
| **Mobile (WiFi)** | `http://{PC_IP}:5000/uploads/logos/{id}/logo.png` |

### Database Storage
```
companies.logo_url = "/uploads/logos/1/logo.png"
```

### Recommended Approach
1. Store relative path in database: `/uploads/logos/1/logo.png`
2. Construct full URL in frontend using `getBaseURL()`
3. Use helper function: `getLogoUrl(company.logo_url)`
4. Display in img src: `<img src={getLogoUrl(company.logo_url)} />`

### Directory Structure
```
/uploads/
  /logos/
    /1/
      logo.png
    /2/
      logo.png
/static/
  logo.jpg (fallback)
```

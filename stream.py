import streamlit as st
import requests
import time
import csv
import pandas as pd
from datetime import datetime

API_KEY = 'AIzaSyAGe4MB8lZcHE4yKlL8Uqt0z3j2VmBqiVk'  # Replace with your API key

# Custom CSS for modern styling
st.set_page_config(
    page_title="Lead Generator Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.2rem;
        margin-bottom: 0;
    }
    
    .search-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .search-container h3 {
        color: #2c3e50;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e8ed;
        padding: 12px 16px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .search-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        color: white;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .search-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stats-card h2 {
        color: white !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem;
    }
    
    .stats-card p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
    
    .download-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        color: white;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
    }
    
    .error-container {
        background: #fff5f5;
        border: 1px solid #fed7d7;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        color: #c53030;
    }
    
    .warning-container {
        background: #fffaf0;
        border: 1px solid #feb2b2;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        color: #c05621;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .metric-card h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

def search_places(query, location, radius=50000):
    endpoint = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': f"{query} in {location}",
        'key': API_KEY
    }

    results = []
    while True:
        res = requests.get(endpoint, params=params).json()
        results.extend(res.get('results', []))
        if 'next_page_token' in res:
            time.sleep(2)
            params['pagetoken'] = res['next_page_token']
        else:
            break
    return results

def get_place_details(place_id):
    endpoint = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,website,formatted_phone_number,rating,user_ratings_total,types',
        'key': API_KEY
    }
    res = requests.get(endpoint, params=params).json()
    return res.get('result', {})

def lead_generation(industry, location):
    raw_places = search_places(industry, location)
    leads = []
    seen = set()

    for place in raw_places:
        place_id = place.get('place_id')
        if not place_id:
            continue

        details = get_place_details(place_id)
        name = details.get('name')
        address = details.get('formatted_address')
        website = details.get('website', '')
        phone = details.get('formatted_phone_number', '')
        rating = details.get('rating', '')
        user_ratings = details.get('user_ratings_total', '')
        types = ', '.join(details.get('types', [])[:3]) if details.get('types') else ''

        key = (name, address)
        if key not in seen:
            seen.add(key)
            leads.append({
                'Company Name': name,
                'Address': address,
                'Website': website,
                'Phone Number': phone,
                'Rating': rating,
                'Total Reviews': user_ratings,
                'Business Type': types
            })

    return leads

def convert_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: white; margin-bottom: 1rem;">🎯 Lead Generator Pro</h2>
        <p style="color: rgba(255,255,255,0.8);">Advanced business lead generation powered by Google Maps API</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    
    # Placeholder metrics - you can make these dynamic
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>Total Searches</h4>
            <p>1,247</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>Leads Found</h4>
            <p>8,934</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    max_results = st.slider("Max Results", 10, 100, 50, help="Maximum number of leads to generate")
    
    st.markdown("---")
    
    st.markdown("### 📞 Support")
    st.markdown("Need help? Contact us at support@leadgenerator.com")

# Main content
st.markdown("""
<div class="main-header">
    <h1>🎯 Lead Generator Pro</h1>
    <p>Discover high-quality business leads with our advanced Google Maps-powered search engine</p>
</div>
""", unsafe_allow_html=True)

# Search Section
st.markdown("""
<div class="search-container">
    <h3>🔍 Search for Business Leads</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    industry_input = st.text_input(
        "🏢 Industry or Business Type",
        placeholder="e.g., IT services, restaurants, pharmacies, real estate",
        help="Enter the type of business you're looking for"
    )

with col2:
    location_input = st.text_input(
        "📍 Location",
        placeholder="e.g., Mumbai, Maharashtra",
        help="Enter the city, state, or region"
    )

# Search button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_clicked = st.button(
        "🚀 Generate Leads",
        use_container_width=True,
        help="Click to start searching for business leads"
    )

# Results Section
if search_clicked:
    if not industry_input or not location_input:
        st.markdown("""
        <div class="warning-container">
            <h4>⚠️ Missing Information</h4>
            <p>Please enter both industry and location to generate leads.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("🔍 Searching Google Maps for businesses..."):
            leads = lead_generation(industry_input, location_input)
        
        if leads:
            # Stats Card
            st.markdown(f"""
            <div class="stats-card">
                <h2>✅ {len(leads)}</h2>
                <p>Businesses found for "{industry_input}" in "{location_input}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Results Container
            st.markdown("""
            <div class="results-container">
                <h3>📋 Generated Leads</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display results in a nice dataframe
            df = pd.DataFrame(leads)
            
            # Format the dataframe for better display
            if not df.empty:
                # Add row numbers
                df.index = range(1, len(df) + 1)
                df.index.name = 'No.'
                
                # Display with custom styling
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=False,
                    column_config={
                        "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                        "Address": st.column_config.TextColumn("Address", width="large"),
                        "Website": st.column_config.LinkColumn("Website", width="medium"),
                        "Phone Number": st.column_config.TextColumn("Phone", width="small"),
                        "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐", width="small"),
                        "Total Reviews": st.column_config.NumberColumn("Reviews", format="%d", width="small"),
                        "Business Type": st.column_config.TextColumn("Type", width="medium")
                    }
                )
                
                # Download Section
                st.markdown("""
                <div class="download-section">
                    <h3>💾 Download Your Leads</h3>
                </div>
                """, unsafe_allow_html=True)
                
                csv = convert_to_csv(leads)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"leads_{industry_input.replace(' ', '_')}_{location_input.replace(' ', '_')}_{timestamp}.csv"
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📥 Download CSV File",
                        data=csv,
                        file_name=filename,
                        mime='text/csv',
                        use_container_width=True,
                        help="Download all leads as a CSV file"
                    )
        else:
            st.markdown("""
            <div class="error-container">
                <h4>❌ No Results Found</h4>
                <p>No businesses found for your search criteria. Try:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Using different keywords</li>
                    <li>Expanding your location search</li>
                    <li>Checking your spelling</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>© 2025 Lead Generator Pro |</p>
    <p>Generate high-quality business leads with confidence</p>
</div>
""", unsafe_allow_html=True)

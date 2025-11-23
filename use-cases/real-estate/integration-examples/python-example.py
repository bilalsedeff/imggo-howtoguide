"""
Real Estate Listing Automation - Python Integration Example
Extract property data from photos and integrate with MLS systems
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_property_photo(image_path: str) -> dict:
    """Process property photo and extract listing data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("REAL_ESTATE_PATTERN_ID", "pat_real_estate_json")

    print(f"\nProcessing property photo: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return json.loads(result) if isinstance(result, str) else result


def enrich_property_data(property_data: dict) -> dict:
    """Enrich property data with calculated fields"""
    enriched = property_data.copy()

    # Calculate price per square foot
    if 'price' in property_data and 'square_feet' in property_data:
        price = float(property_data['price'])
        sqft = float(property_data['square_feet'])
        if sqft > 0:
            enriched['price_per_sqft'] = round(price / sqft, 2)

    # Determine property category
    if 'property_type' in property_data:
        prop_type = property_data['property_type'].lower()
        if 'condo' in prop_type or 'apartment' in prop_type:
            enriched['category'] = 'Multi-Family'
        elif 'commercial' in prop_type:
            enriched['category'] = 'Commercial'
        elif 'land' in prop_type or 'lot' in prop_type:
            enriched['category'] = 'Land'
        else:
            enriched['category'] = 'Single-Family'

    # Calculate estimated monthly payment (simplified)
    if 'price' in property_data:
        price = float(property_data['price'])
        # Assume 20% down, 30-year mortgage, 7% interest
        loan_amount = price * 0.8
        monthly_rate = 0.07 / 12
        num_payments = 30 * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        enriched['estimated_monthly_payment'] = round(monthly_payment, 2)

    return enriched


def validate_listing(property_data: dict) -> dict:
    """Validate property listing data"""
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Required fields
    required_fields = ['address', 'price', 'bedrooms', 'bathrooms', 'square_feet']

    for field in required_fields:
        if field not in property_data or not property_data[field]:
            validation['is_valid'] = False
            validation['errors'].append(f"Missing required field: {field}")

    # Data validation
    if 'price' in property_data:
        try:
            price = float(property_data['price'])
            if price <= 0:
                validation['errors'].append("Price must be greater than zero")
                validation['is_valid'] = False
            elif price < 10000:
                validation['warnings'].append(f"Unusually low price: ${price:,.2f}")
        except (ValueError, TypeError):
            validation['errors'].append("Invalid price format")
            validation['is_valid'] = False

    if 'square_feet' in property_data:
        try:
            sqft = float(property_data['square_feet'])
            if sqft <= 0:
                validation['errors'].append("Square feet must be greater than zero")
                validation['is_valid'] = False
            elif sqft < 200:
                validation['warnings'].append(f"Unusually small property: {sqft} sqft")
        except (ValueError, TypeError):
            validation['errors'].append("Invalid square feet format")
            validation['is_valid'] = False

    # Check for photos
    if 'photos' in property_data:
        photo_count = len(property_data.get('photos', []))
        if photo_count == 0:
            validation['warnings'].append("No property photos - listings with photos get 95% more views")
        elif photo_count < 5:
            validation['warnings'].append(f"Only {photo_count} photos - consider adding more")

    return validation


def generate_mls_listing(property_data: dict) -> dict:
    """Generate MLS-compatible listing"""
    mls_listing = {
        'ListingID': property_data.get('listing_id'),
        'StandardStatus': 'Active',
        'ListPrice': property_data.get('price'),
        'UnparsedAddress': property_data.get('address'),
        'City': property_data.get('city'),
        'StateOrProvince': property_data.get('state'),
        'PostalCode': property_data.get('zip_code'),
        'PropertyType': property_data.get('property_type'),
        'PropertySubType': property_data.get('property_subtype'),
        'BedroomsTotal': property_data.get('bedrooms'),
        'BathroomsTotalInteger': property_data.get('bathrooms'),
        'LivingArea': property_data.get('square_feet'),
        'LotSizeSquareFeet': property_data.get('lot_size'),
        'YearBuilt': property_data.get('year_built'),
        'PublicRemarks': property_data.get('description'),
        'Media': [],
    }

    # Add photos
    if 'photos' in property_data:
        for i, photo_url in enumerate(property_data['photos']):
            mls_listing['Media'].append({
                'MediaURL': photo_url,
                'Order': i + 1,
                'MediaCategory': 'Photo'
            })

    # Add features
    if 'features' in property_data:
        mls_listing['Features'] = property_data['features']

    return mls_listing


def save_to_mls_system(mls_listing: dict) -> bool:
    """Save listing to MLS system"""
    print("\n" + "="*60)
    print("SAVING TO MLS SYSTEM")
    print("="*60)

    # In production, integrate with MLS RETS/RESO API
    # Examples: ListHub, Zillow Bridge Interactive, MLSGrid

    print("MLS Listing Data:")
    print(json.dumps(mls_listing, indent=2))

    # Simulate API call
    # response = requests.post('https://mls-api.example.com/listings', json=mls_listing)

    print("\n✓ Listing saved to MLS (simulated)")
    return True


def sync_to_portals(property_data: dict) -> List[str]:
    """Sync listing to real estate portals"""
    print("\n" + "="*60)
    print("SYNCING TO REAL ESTATE PORTALS")
    print("="*60)

    portals = ['Zillow', 'Realtor.com', 'Trulia', 'Redfin']
    synced_portals = []

    for portal in portals:
        print(f"  Syncing to {portal}...")

        # In production, use portal-specific APIs
        # Zillow: Bridge Interactive API
        # Realtor.com: Move, Inc. API
        # Trulia: Part of Zillow Group

        # Simulate sync
        synced_portals.append(portal)
        print(f"    ✓ {portal} sync completed")

    return synced_portals


def generate_listing_description(property_data: dict) -> str:
    """Generate compelling listing description using AI"""
    # In production, this could use GPT-4 or similar
    # For now, generate a template-based description

    address = property_data.get('address', 'this beautiful property')
    bedrooms = property_data.get('bedrooms', 'N/A')
    bathrooms = property_data.get('bathrooms', 'N/A')
    sqft = property_data.get('square_feet', 'N/A')
    price = property_data.get('price', 'N/A')

    description_parts = []

    # Opening
    if isinstance(price, (int, float)):
        description_parts.append(f"Welcome to {address}, offered at ${price:,.0f}.")
    else:
        description_parts.append(f"Welcome to {address}.")

    # Details
    if bedrooms and bathrooms and sqft:
        description_parts.append(
            f"This stunning {bedrooms} bedroom, {bathrooms} bathroom home features "
            f"{sqft:,.0f} square feet of beautifully designed living space."
        )

    # Features
    if 'features' in property_data:
        features = property_data['features']
        if isinstance(features, list) and len(features) > 0:
            feature_str = ', '.join(features[:5])
            description_parts.append(f"Enjoy premium amenities including {feature_str}.")

    # Location
    if 'city' in property_data:
        description_parts.append(
            f"Conveniently located in {property_data['city']}, "
            f"close to shopping, dining, and entertainment."
        )

    # Call to action
    description_parts.append("Schedule your showing today!")

    return " ".join(description_parts)


def main():
    print("="*60)
    print("REAL ESTATE LISTING AUTOMATION - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "real-estate1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        print("Using placeholder for demonstration")
        # In production, handle missing file
        sys.exit(1)

    try:
        # Process property photo
        property_data = process_property_photo(str(test_image))

        # Save raw JSON
        output_file = "property_data.json"
        with open(output_file, 'w') as f:
            json.dump(property_data, f, indent=2)
        print(f"\n✓ Saved property data to {output_file}")

        # Enrich data
        enriched_data = enrich_property_data(property_data)

        print("\n" + "="*60)
        print("PROPERTY DETAILS")
        print("="*60)
        print(f"Address: {enriched_data.get('address')}")
        print(f"City: {enriched_data.get('city')}, {enriched_data.get('state')} {enriched_data.get('zip_code')}")
        print(f"Price: ${enriched_data.get('price', 0):,.2f}")
        print(f"Bedrooms: {enriched_data.get('bedrooms')}")
        print(f"Bathrooms: {enriched_data.get('bathrooms')}")
        print(f"Square Feet: {enriched_data.get('square_feet'):,}")

        if 'price_per_sqft' in enriched_data:
            print(f"Price/SqFt: ${enriched_data['price_per_sqft']}")

        if 'estimated_monthly_payment' in enriched_data:
            print(f"Est. Monthly Payment: ${enriched_data['estimated_monthly_payment']:,.2f}")

        # Validate listing
        validation = validate_listing(enriched_data)

        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(f"Valid: {'✓' if validation['is_valid'] else '✗'}")

        if validation['errors']:
            print(f"\nErrors ({len(validation['errors'])}):")
            for error in validation['errors']:
                print(f"  ✗ {error}")

        if validation['warnings']:
            print(f"\nWarnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")

        if validation['is_valid']:
            # Generate listing description
            description = generate_listing_description(enriched_data)

            print("\n" + "="*60)
            print("GENERATED LISTING DESCRIPTION")
            print("="*60)
            print(description)

            # Generate MLS listing
            enriched_data['description'] = description
            mls_listing = generate_mls_listing(enriched_data)

            # Save to MLS
            save_to_mls_system(mls_listing)

            # Sync to portals
            synced_portals = sync_to_portals(enriched_data)

            print("\n" + "="*60)
            print("SYNDICATION COMPLETE")
            print("="*60)
            print(f"Listing published to {len(synced_portals)} portals:")
            for portal in synced_portals:
                print(f"  ✓ {portal}")

            # Save MLS listing
            mls_file = "mls_listing.json"
            with open(mls_file, 'w') as f:
                json.dump(mls_listing, f, indent=2)
            print(f"\n✓ Saved MLS listing to {mls_file}")

        else:
            print("\n⚠ Listing requires corrections before publishing")

        print("\n✓ Real estate listing automation completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

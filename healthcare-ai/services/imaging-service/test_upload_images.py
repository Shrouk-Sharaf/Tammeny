# services/imaging-service/test_upload_images.py
import requests
import os
from PIL import Image
import io

def test_with_uploaded_images():
    print("X-Ray Model - Image Upload Test")
    print("=" * 50)
    
    test_images = [
        r"D:\SIC-GraduationProject\IM-0001-0001.jpeg", 
        r"D:\SIC-GraduationProject\IM-0119-0001.jpeg", 
        r"D:\SIC-GraduationProject\person1000_bacteria_2931.jpeg"
    ]
    
    # Filter to only existing images
    existing_images = [img for img in test_images if os.path.exists(img)]
    
    if not existing_images:
        print("No test images found at the specified paths!")
        print("\nPlease modify the 'test_images' list in the script to point to your actual image files")
        print("Or let me create some test images for you...")
        create_test_images()
        return
    
    print(f"Found {len(existing_images)} images to analyze")
    
    # Analyze each image
    for i, image_path in enumerate(existing_images, 1):
        print(f"\n{'='*50}")
        print(f"Image {i}/{len(existing_images)}: {os.path.basename(image_path)}")
        analyze_single_image(image_path)
    
    print(f"\n{'='*50}")
    print("Image Upload Test Complete!")
    print("Your X-Ray model is ready to analyze uploaded images!")

def analyze_single_image(image_path):
    """Analyze a single uploaded image"""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(
                'http://localhost:8002/analyze/xray', 
                files=files,
                data={'confidence_threshold': 0.1}
            )
        
        if response.status_code == 200:
            results = response.json()
            
            print(f"✅ ANALYSIS SUCCESSFUL!")
            print(f"Analysis ID: {results['analysis_id']}")
            print(f"Overall Risk: {results['overall_risk_level'].upper()}")
            
            summary = results['findings_summary']
            print(f"Findings Summary:")
            print(f"   Total: {summary['total_findings']}")
            print(f"   High Severity: {summary['high_severity']}")
            print(f"   Medium Severity: {summary['medium_severity']}")
            print(f"   Low Severity: {summary['low_severity']}")
            
            # Show detailed findings
            print(f"\nDetailed Findings:")
            for severity in ['high_severity', 'medium_severity', 'low_severity']:
                findings = results['detailed_findings'][severity]
                if findings:
                    severity_display = severity.replace('_', ' ').title()
                    emoji = '🚨' if severity == 'high_severity' else '⚠️' if severity == 'medium_severity' else 'ℹ️'
                    print(f"\n   {emoji} {severity_display}:")
                    for finding in findings[:3]:  # Show top 3 per category
                        print(f"      - {finding['condition']}: {finding['confidence_percent']}")
                        if 'medical_advice' in finding and severity != 'low_severity':
                            print(f"        {finding['medical_advice']}")
            
            # Recommendations
            print(f"\nClinical Recommendations:")
            for j, rec in enumerate(results['clinical_recommendations'], 1):
                print(f"   {j}. {rec}")
                
        else:
            print(f"Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"Error analyzing image: {e}")

def create_test_images():
    """Create some test X-ray images if no real images are available"""
    print("\nCreating test X-ray images...")
    
    test_images_created = []
    
    # Create different types of test images
    test_cases = [
        ('normal_chest.jpg', 'Normal chest X-ray simulation', 60),
        ('mild_abnormal.jpg', 'Mild abnormality simulation', 100),
        ('moderate_abnormal.jpg', 'Moderate abnormality simulation', 140),
    ]
    
    for filename, description, brightness in test_cases:
        # Create image
        img = Image.new('L', (224, 224), color=brightness)
        
        # Add some variation to make it more interesting
        if 'abnormal' in filename:
            # Add some bright spots for abnormalities
            for x in range(80, 160):
                for y in range(80, 160):
                    if (x + y) % 20 == 0:  # Pattern
                        img.putpixel((x, y), min(255, brightness + 80))
        
        # Save image
        save_path = os.path.join(os.getcwd(), filename)
        img.save(save_path)
        test_images_created.append(save_path)
        print(f"Created: {filename} - {description}")
    
    print(f"\nCreated {len(test_images_created)} test images in current directory")
    print("Now analyzing the created test images...")
    
    # Analyze the created images
    for image_path in test_images_created:
        print(f"\n{'='*50}")
        print(f"Analyzing: {os.path.basename(image_path)}")
        analyze_single_image(image_path)
    
    # Cleanup option
    print(f"\n{'='*50}")
    cleanup = input("Delete test images? (y/n): ").lower().strip()
    if cleanup == 'y':
        for image_path in test_images_created:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Deleted: {os.path.basename(image_path)}")

def upload_single_image():
    """Upload and analyze a single specific image"""
    print("\nSingle Image Upload")
    print("=" * 30)
    
    # Get image path from user
    image_path = input("Enter the full path to your X-ray image: ").strip()
    
    # Remove quotes if user pasted path with quotes
    image_path = image_path.strip('"\'')
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    print(f"Analyzing: {os.path.basename(image_path)}")
    analyze_single_image(image_path)

if __name__ == "__main__":
    print("Choose test option:")
    print("1. Test with pre-defined image paths")
    print("2. Upload a single specific image")
    print("3. Create and test with generated images")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        test_with_uploaded_images()
    elif choice == "2":
        upload_single_image()
    elif choice == "3":
        create_test_images()
    else:
        print("Invalid choice. Running default test...")
        test_with_uploaded_images()
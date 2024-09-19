from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# The URL you want to fetch
BASE_URL = "https://www.sefi.pf/SefiWeb/SefiOffres.nsf/RechercheOffreWeb1?SearchView&Query=%28%28%5BIle%5D%3DTAHITI%29%29&SearchOrder=4"
OUTPUT_FILE = "cleaned_job_posts.txt"

def fetch_jobs_with_selenium(url):
    # Set up the ChromeDriver path using Service
    service = Service('./chromedriver')

    # Initialize the WebDriver with the Service object
    driver = webdriver.Chrome(service=service)

    # Open the URL
    driver.get(url)

    # Wait for the page to fully load
    time.sleep(5)  # Adjust the sleep time if necessary

    all_page_sources = []

    # Loop through all pages and capture the HTML content
    while True:
        # Get the page source after the JavaScript has executed
        page_source = driver.page_source
        all_page_sources.append(page_source)

        # Check if there is a "Next" button and if it's clickable
        try:
            next_button = driver.find_element(By.LINK_TEXT, 'Suivant >')  # Adjust the text for "Next"

            # Use JavaScript to check if the button is still enabled
            is_disabled = driver.execute_script("return arguments[0].disabled;", next_button)
            
            if is_disabled:
                print("The 'Next' button is disabled, stopping.")
                break

            # Store the current page content to compare later
            old_content = driver.page_source

            # Click the next button to go to the next page
            next_button.click()
            time.sleep(3)  # Wait for the next page to load

            # Check if the page content has changed
            new_content = driver.page_source
            if new_content == old_content:
                print("The content did not change after clicking 'Next', stopping.")
                break

        except:
            # If no "Next" button is found, stop the loop
            print("No 'Next' button found, stopping.")
            break

    # Close the browser
    driver.quit()

    return all_page_sources

# Function to extract and clean job posts
def extract_job_posts(html_content_list):
    job_posts = []

    # Loop through the list of page sources
    for html_content in html_content_list:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all job entries
        job_entries = soup.find_all('tr', align='left')

        for entry in job_entries:
            title_tag = entry.find("font", class_="titreBleu")
            if title_tag:
                # Extract job title and reference number
                title_text = title_tag.get_text(strip=True)
                ref_number = title_text.split(":")[0] if ":" in title_text else "N/A"
                title = title_text.split(":")[1].strip() if ":" in title_text else title_text

                # Extract description
                description_tag = entry.find_all("font", class_="textPetit")
                description = ' '.join([d.get_text(strip=True) for d in description_tag])

                # Extract the link to the job offer
                link_tag = entry.find('a', href=True)
                job_link = f"https://www.sefi.pf{link_tag['href']}" if link_tag else "No link available"

                # Clean and format the job post
                job_posts.append(f"Reference: {ref_number}\nTitle: {title}\nDescription: {description}\nLink: {job_link}\n")

    return job_posts

# Function to save the cleaned job posts to a file
def save_job_posts(job_posts, filename=OUTPUT_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        for post in job_posts:
            f.write(post + "\n\n")
    print(f"Saved {len(job_posts)} job posts to {filename}")

def main():
    # Fetch the HTML content with Selenium (including pagination)
    all_page_sources = fetch_jobs_with_selenium(BASE_URL)
    
    # Extract and clean the job posts from the HTML content
    job_posts = extract_job_posts(all_page_sources)
    
    # Save the cleaned job posts
    save_job_posts(job_posts)

if __name__ == "__main__":
    main()

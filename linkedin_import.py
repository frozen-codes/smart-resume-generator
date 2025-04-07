"""
LinkedIn Import Module for Resume Generator
Handles importing data from LinkedIn profile exports
"""

import json
import csv
import os
import re
import datetime
from collections import defaultdict

def parse_linkedin_json(file_path):
    """
    Parse LinkedIn profile data from a JSON export file
    
    Args:
        file_path: Path to the LinkedIn JSON export file
        
    Returns:
        dict: Structured LinkedIn profile data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Initialize profile data structure
        profile = {
            'name': '',
            'job_role': '',
            'summary': '',
            'location': '',
            'skills': [],
            'experience': [],
            'education': [],
            'contact_info': {},
            'years_experience': 0
        }
        
        # Extract basic profile info
        if 'profile' in data:
            profile_data = data['profile']
            
            # Name
            if 'firstName' in profile_data and 'lastName' in profile_data:
                profile['name'] = f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".strip()
            
            # Current job role
            if 'headline' in profile_data:
                profile['job_role'] = profile_data.get('headline', '')
            
            # Summary
            if 'summary' in profile_data:
                profile['summary'] = profile_data.get('summary', '')
            
            # Location
            if 'geoLocation' in profile_data and 'name' in profile_data['geoLocation']:
                profile['location'] = profile_data['geoLocation']['name']
            elif 'locationName' in profile_data:
                profile['location'] = profile_data.get('locationName', '')
        
        # Extract skills
        if 'skills' in data:
            for skill in data['skills']:
                skill_name = skill.get('name', '')
                if skill_name:
                    profile['skills'].append(skill_name)
        
        # Extract experience
        if 'positions' in data:
            for position in data['positions']:
                job = {
                    'title': position.get('title', ''),
                    'company': position.get('companyName', ''),
                    'description': position.get('description', ''),
                    'start_date': '',
                    'end_date': '',
                    'duration': ''
                }
                
                # Format dates
                if 'startDate' in position:
                    start_date = position['startDate']
                    job['start_date'] = f"{start_date.get('month', '')}/{start_date.get('year', '')}"
                
                if 'endDate' in position:
                    end_date = position['endDate']
                    job['end_date'] = f"{end_date.get('month', '')}/{end_date.get('year', '')}"
                else:
                    job['end_date'] = 'Present'
                
                # Duration
                if 'durationInMonths' in position:
                    months = position['durationInMonths']
                    years = months // 12
                    remaining_months = months % 12
                    
                    if years > 0:
                        job['duration'] = f"{years} year{'s' if years > 1 else ''}"
                        if remaining_months > 0:
                            job['duration'] += f", {remaining_months} month{'s' if remaining_months > 1 else ''}"
                    else:
                        job['duration'] = f"{remaining_months} month{'s' if remaining_months > 1 else ''}"
                
                profile['experience'].append(job)
        
        # Extract education
        if 'education' in data:
            for edu in data['education']:
                education = {
                    'school': edu.get('schoolName', ''),
                    'degree': edu.get('degreeName', ''),
                    'field': edu.get('fieldOfStudy', ''),
                    'start_date': '',
                    'end_date': ''
                }
                
                # Format dates
                if 'startDate' in edu and 'year' in edu['startDate']:
                    education['start_date'] = str(edu['startDate']['year'])
                
                if 'endDate' in edu and 'year' in edu['endDate']:
                    education['end_date'] = str(edu['endDate']['year'])
                
                profile['education'].append(education)
        
        # Extract contact info
        if 'profile' in data:
            profile_data = data['profile']
            
            contact_info = {}
            if 'phoneNumbers' in profile_data:
                for phone in profile_data['phoneNumbers']:
                    contact_info['phone'] = phone.get('number', '')
                    break  # Just take the first one
            
            if 'emailAddress' in profile_data:
                contact_info['email'] = profile_data['emailAddress']
            
            if 'websites' in profile_data:
                websites = []
                for website in profile_data['websites']:
                    if 'url' in website:
                        websites.append(website['url'])
                
                if websites:
                    contact_info['websites'] = websites
            
            profile['contact_info'] = contact_info
        
        # Calculate total years of experience
        profile['years_experience'] = extract_years_of_experience(profile['experience'])
        
        return profile
    
    except Exception as e:
        raise Exception(f"Error parsing LinkedIn JSON: {str(e)}")

def parse_linkedin_csv(file_path):
    """
    Parse LinkedIn profile data from a CSV export file
    
    Args:
        file_path: Path to the LinkedIn CSV export file
        
    Returns:
        dict: Structured LinkedIn profile data
    """
    try:
        # Determine what kind of CSV file this is by checking the filename
        filename = os.path.basename(file_path).lower()
        
        # Initialize profile data structure
        profile = {
            'name': '',
            'job_role': '',
            'summary': '',
            'location': '',
            'skills': [],
            'experience': [],
            'education': [],
            'contact_info': {},
            'years_experience': 0
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            headers = next(csv_reader)  # Read headers
            
            # Check file type based on headers
            if 'First Name' in headers and 'Last Name' in headers:
                # Profile information
                row = next(csv_reader, None)  # Get the first data row
                if row:
                    first_name_idx = headers.index('First Name')
                    last_name_idx = headers.index('Last Name')
                    profile['name'] = f"{row[first_name_idx]} {row[last_name_idx]}".strip()
                    
                    # Current position
                    if 'Headline' in headers:
                        headline_idx = headers.index('Headline')
                        profile['job_role'] = row[headline_idx]
                    
                    # Summary
                    if 'Summary' in headers:
                        summary_idx = headers.index('Summary')
                        profile['summary'] = row[summary_idx]
                    
                    # Location
                    if 'Location' in headers:
                        location_idx = headers.index('Location')
                        profile['location'] = row[location_idx]
                    
                    # Contact info
                    contact_info = {}
                    if 'Email Address' in headers:
                        email_idx = headers.index('Email Address')
                        contact_info['email'] = row[email_idx]
                    
                    if 'Phone Numbers' in headers:
                        phone_idx = headers.index('Phone Numbers')
                        contact_info['phone'] = row[phone_idx]
                    
                    profile['contact_info'] = contact_info
            
            elif 'Company Name' in headers and 'Title' in headers:
                # Experience information
                for row in csv_reader:
                    if not row or not any(row):  # Skip empty rows
                        continue
                    
                    company_idx = headers.index('Company Name')
                    title_idx = headers.index('Title')
                    
                    job = {
                        'company': row[company_idx],
                        'title': row[title_idx],
                        'description': '',
                        'start_date': '',
                        'end_date': '',
                        'duration': ''
                    }
                    
                    # Description
                    if 'Description' in headers:
                        desc_idx = headers.index('Description')
                        job['description'] = row[desc_idx]
                    
                    # Dates
                    if 'Started On' in headers:
                        start_idx = headers.index('Started On')
                        job['start_date'] = row[start_idx]
                    
                    if 'Finished On' in headers:
                        end_idx = headers.index('Finished On')
                        job['end_date'] = row[end_idx] if row[end_idx] else 'Present'
                    
                    profile['experience'].append(job)
            
            elif 'School Name' in headers and 'Degree Name' in headers:
                # Education information
                for row in csv_reader:
                    if not row or not any(row):  # Skip empty rows
                        continue
                    
                    school_idx = headers.index('School Name')
                    degree_idx = headers.index('Degree Name')
                    
                    education = {
                        'school': row[school_idx],
                        'degree': row[degree_idx],
                        'field': '',
                        'start_date': '',
                        'end_date': ''
                    }
                    
                    # Field of study
                    if 'Field of Study' in headers:
                        field_idx = headers.index('Field of Study')
                        education['field'] = row[field_idx]
                    
                    # Dates
                    if 'Started On' in headers:
                        start_idx = headers.index('Started On')
                        education['start_date'] = row[start_idx]
                    
                    if 'Finished On' in headers:
                        end_idx = headers.index('Finished On')
                        education['end_date'] = row[end_idx]
                    
                    profile['education'].append(education)
            
            elif 'Skill Name' in headers:
                # Skills information
                skill_idx = headers.index('Skill Name')
                for row in csv_reader:
                    if not row or not any(row):  # Skip empty rows
                        continue
                    profile['skills'].append(row[skill_idx])
        
        # Calculate total years of experience if we have experience data
        if profile['experience']:
            profile['years_experience'] = extract_years_of_experience(profile['experience'])
        
        return profile
    
    except Exception as e:
        raise Exception(f"Error parsing LinkedIn CSV: {str(e)}")

def combine_profile_data(file_paths):
    """
    Combine data from multiple LinkedIn export files
    
    Args:
        file_paths: List of paths to LinkedIn export files
        
    Returns:
        dict: Combined LinkedIn profile data
    """
    combined_profile = {
        'name': '',
        'job_role': '',
        'summary': '',
        'location': '',
        'skills': [],
        'experience': [],
        'education': [],
        'contact_info': {},
        'years_experience': 0
    }
    
    for file_path in file_paths:
        try:
            # Parse the file based on extension
            if file_path.lower().endswith('.json'):
                profile = parse_linkedin_json(file_path)
            elif file_path.lower().endswith('.csv'):
                profile = parse_linkedin_csv(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                continue
            
            # Merge data
            if not combined_profile['name'] and profile['name']:
                combined_profile['name'] = profile['name']
            
            if not combined_profile['job_role'] and profile['job_role']:
                combined_profile['job_role'] = profile['job_role']
            
            if not combined_profile['summary'] and profile['summary']:
                combined_profile['summary'] = profile['summary']
            
            if not combined_profile['location'] and profile['location']:
                combined_profile['location'] = profile['location']
            
            # Combine skills without duplicates
            for skill in profile['skills']:
                if skill not in combined_profile['skills']:
                    combined_profile['skills'].append(skill)
            
            # Combine experience entries
            for exp in profile['experience']:
                if exp not in combined_profile['experience']:
                    combined_profile['experience'].append(exp)
            
            # Combine education entries
            for edu in profile['education']:
                if edu not in combined_profile['education']:
                    combined_profile['education'].append(edu)
            
            # Combine contact info
            for key, value in profile['contact_info'].items():
                if key not in combined_profile['contact_info']:
                    combined_profile['contact_info'][key] = value
            
            # Update years of experience if the new value is greater
            if profile['years_experience'] > combined_profile['years_experience']:
                combined_profile['years_experience'] = profile['years_experience']
        
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    return combined_profile

def format_experience_for_resume(experiences):
    """
    Format experience data for resume presentation
    
    Args:
        experiences: List of experience dictionaries
        
    Returns:
        str: Formatted experience section for resume
    """
    if not experiences:
        return ""
    
    # Sort experiences by date (most recent first)
    sorted_exp = sorted(
        experiences, 
        key=lambda x: datetime.datetime.now() if x['end_date'] == 'Present' else 
            datetime.datetime.strptime(x['end_date'].split('/')[-1], '%Y') 
            if '/' in x['end_date'] else x['end_date'],
        reverse=True
    )
    
    formatted_text = ""
    for exp in sorted_exp:
        # Format dates
        date_range = f"{exp['start_date']} - {exp['end_date']}"
        
        # Format position
        formatted_text += f"**{exp['title']}** at *{exp['company']}* ({date_range})\n\n"
        
        # Add description if available
        if exp['description']:
            formatted_text += f"{exp['description']}\n\n"
    
    return formatted_text

def format_education_for_resume(education):
    """
    Format education data for resume presentation
    
    Args:
        education: List of education dictionaries
        
    Returns:
        str: Formatted education section for resume
    """
    if not education:
        return ""
    
    # Sort education by date (most recent first)
    sorted_edu = sorted(
        education, 
        key=lambda x: int(x['end_date']) if x['end_date'].isdigit() else 0, 
        reverse=True
    )
    
    formatted_text = ""
    for edu in sorted_edu:
        # Format degree and field
        degree_field = edu['degree']
        if edu['field'] and edu['field'] not in edu['degree']:
            degree_field += f", {edu['field']}"
        
        # Format date range
        date_range = ""
        if edu['start_date'] or edu['end_date']:
            date_range = f" ({edu['start_date']} - {edu['end_date']})"
        
        formatted_text += f"**{degree_field}** from *{edu['school']}*{date_range}\n\n"
    
    return formatted_text

def extract_years_of_experience(experiences):
    """
    Extract the total years of experience from the provided experience data
    
    Args:
        experiences: List of experience dictionaries
        
    Returns:
        int: Total years of experience
    """
    total_months = 0
    
    for exp in experiences:
        # Handle different date formats
        try:
            # Try to get start and end dates
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            # If no dates are available, skip this entry
            if not start_date:
                continue
            
            # Process start date
            if '/' in start_date:
                # Format MM/YYYY
                start_parts = start_date.split('/')
                if len(start_parts) == 2:
                    start_year = int(start_parts[1])
                    start_month = int(start_parts[0])
                else:
                    continue
            else:
                # Just year
                try:
                    start_year = int(start_date)
                    start_month = 1  # Default to January
                except ValueError:
                    continue
            
            # Process end date
            if end_date == 'Present':
                # Use current date for "Present"
                now = datetime.datetime.now()
                end_year = now.year
                end_month = now.month
            elif '/' in end_date:
                # Format MM/YYYY
                end_parts = end_date.split('/')
                if len(end_parts) == 2:
                    end_year = int(end_parts[1])
                    end_month = int(end_parts[0])
                else:
                    continue
            else:
                # Just year
                try:
                    end_year = int(end_date)
                    end_month = 12  # Default to December
                except ValueError:
                    continue
            
            # Calculate duration in months
            duration_months = (end_year - start_year) * 12 + (end_month - start_month + 1)
            total_months += max(0, duration_months)  # Ensure non-negative
        
        except Exception:
            # If there's any error in parsing dates, skip this entry
            continue
    
    # Convert total months to years (rounded down)
    return total_months // 12 
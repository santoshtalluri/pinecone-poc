def format_job_details(job_details):
    return f"""
    <h2>Job Title: {job_details.get('job_title', 'N/A')}</h2>
    <h3>Company: {job_details.get('company_name', 'N/A')}</h3>
    <p><strong>Location:</strong> {job_details.get('location', 'N/A')}</p>
    """
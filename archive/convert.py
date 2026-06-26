import re
import os

def convert_html_to_jsx(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        return ""
    
    body = body_match.group(1)
    
    # remove HTML comments
    body = re.sub(r'<!--(.*?)-->', '', body, flags=re.DOTALL)
    
    # remove <script> tags
    body = re.sub(r'<script.*?>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    
    # replace attributes
    replacements = [
        ('class=', 'className='),
        ('onclick=', 'onClick='),
        ('for=', 'htmlFor='),
        ('tabindex=', 'tabIndex='),
        ('stroke-width=', 'strokeWidth='),
        ('stroke-linecap=', 'strokeLinecap='),
        ('stroke-linejoin=', 'strokeLinejoin='),
        ('autoplay=', 'autoPlay='),
        ('playsinline=', 'playsInline='),
        ('readonly=', 'readOnly='),
        ('readOnly=""', 'readOnly={true}'),
        ('checked=""', 'defaultChecked={true}'),
        ('checked', 'defaultChecked={true}')
    ]
    for old, new in replacements:
        body = body.replace(old, new)
        
    # remove onclick string handlers because they cause TSX errors.
    body = re.sub(r'onClick="[^"]*"', '', body)
    
    # remove style string handlers because they cause TSX errors.
    body = re.sub(r'style="[^"]*"', '', body)
    
    # close img tags
    body = re.sub(r'<img([^>]*?)(?<!/)>', r'<img\1 />', body)
    
    # close input tags
    body = re.sub(r'<input([^>]*?)(?<!/)>', r'<input\1 />', body)
    
    # close br tags
    body = re.sub(r'<br([^>]*?)(?<!/)>', r'<br\1 />', body)

    return body

pages = [
    ('home.html', 'apps/web/src/app/page.tsx', 'Home'),
    ('search.html', 'apps/web/src/app/search/page.tsx', 'Search'),
    ('results.html', 'apps/web/src/app/results/page.tsx', 'Results'),
    ('emergency.html', 'apps/web/src/app/emergency/page.tsx', 'Emergency'),
    ('profile.html', 'apps/web/src/app/profile/page.tsx', 'Profile'),
]

for html_file, tsx_file, component_name in pages:
    jsx = convert_html_to_jsx(f'stitch_new/{html_file}')
    if not jsx:
        continue
    
    use_client = '"use client";\n\n'
    
    react_code = f"""{use_client}import React from 'react';
import Link from 'next/link';

export default function {component_name}Page() {{
  const toggleSidebar = () => {{
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('side-nav-overlay');
    if (sidebar && overlay) {{
      sidebar.classList.toggle('-translate-x-full');
      overlay.classList.toggle('hidden');
      setTimeout(() => overlay.classList.toggle('opacity-0'), 10);
    }}
  }};

  return (
    <>
      {jsx}
    </>
  );
}}
"""
    os.makedirs(os.path.dirname(tsx_file), exist_ok=True)
    with open(tsx_file, 'w', encoding='utf-8') as f:
        f.write(react_code)
        
    print(f"Converted {html_file} -> {tsx_file}")


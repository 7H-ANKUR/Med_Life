import re

def html_to_jsx(html):
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.IGNORECASE | re.DOTALL)
    if body_match:
        content = body_match.group(1)
    else:
        content = html

    # Convert class to className
    content = content.replace('class="', 'className="')
    content = content.replace('for="', 'htmlFor="')
    
    # Convert HTML comments to JSX comments
    content = re.sub(r'<!--(.*?)-->', r'{/* \1 */}', content, flags=re.DOTALL)

    # Make sure img, input, hr are self-closing
    content = re.sub(r'<(img|input|hr|br)([^>]*?)(?<!/)>', r'<\1\2 />', content)

    # Some SVG props might need conversion
    svg_attrs = {
        'stroke-width': 'strokeWidth',
        'stroke-linecap': 'strokeLinecap',
        'stroke-linejoin': 'strokeLinejoin',
        'fill-rule': 'fillRule',
        'clip-rule': 'clipRule',
        'stroke-miterlimit': 'strokeMiterlimit'
    }
    for old, new in svg_attrs.items():
        content = content.replace(old + '="', new + '="')
        
    # Replace inline styles (naive approach, handles simple ones)
    def style_replacer(match):
        style_str = match.group(1)
        styles = {}
        for rule in style_str.split(';'):
            rule = rule.strip()
            if not rule:
                continue
            if ':' in rule:
                key, val = rule.split(':', 1)
                key = key.strip()
                val = val.strip()
                # camelCase key
                key_parts = key.split('-')
                key = key_parts[0] + ''.join(p.title() for p in key_parts[1:])
                styles[key] = val
        
        style_obj_str = ', '.join([f"'{k}': '{v}'" for k, v in styles.items()])
        return f"style={{{{ {style_obj_str} }}}}"
        
    content = re.sub(r'style="([^"]*)"', style_replacer, content)

    return content

with open(r'C:\Users\ankur\Documents\projects\med\stitch_travelmed_ai_healthcare_finder\profile_medlife\code.html', 'r', encoding='utf-8') as f:
    html = f.read()

jsx_content = html_to_jsx(html)

react_component = f"""'use client'

import React, {{ useState }} from 'react'
import Link from 'next/link'

export default function ProfilePage() {{
  return (
    <div className="bg-surface text-on-surface min-h-screen">
      {{/* Rendered from Stitch */}}
      {jsx_content}
    </div>
  )
}}
"""

with open(r'C:\Users\ankur\Documents\projects\med\travel-health-finder\apps\web\src\app\profile\page.tsx', 'w', encoding='utf-8') as f:
    f.write(react_component)

print('Successfully converted HTML to JSX and updated profile page')

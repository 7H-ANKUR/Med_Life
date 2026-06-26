import re

file_path = 'apps/web/src/app/page.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Sidebar Links
content = content.replace('href="#">\n<span className="material-symbols-outlined group-hover:text-primary">search</span>', 'href="/search">\n<span className="material-symbols-outlined group-hover:text-primary">search</span>')
content = content.replace('href="#">\n<span className="material-symbols-outlined group-hover:text-primary">bookmark</span>', 'href="/saved">\n<span className="material-symbols-outlined group-hover:text-primary">bookmark</span>')
content = content.replace('href="#">\n<span className="material-symbols-outlined group-hover:text-primary">history</span>', 'href="/history">\n<span className="material-symbols-outlined group-hover:text-primary">history</span>')
content = content.replace('href="#">\n<span className="material-symbols-outlined group-hover:text-primary">person</span>', 'href="/profile">\n<span className="material-symbols-outlined group-hover:text-primary">person</span>')
content = content.replace('href="#">\n<span className="material-symbols-outlined">settings</span>', 'href="/profile">\n<span className="material-symbols-outlined">settings</span>')
content = content.replace('href="#">\n<span className="material-symbols-outlined">logout</span>', 'href="/login">\n<span className="material-symbols-outlined">logout</span>')

# Replace Buttons in Main Content
# Book Consultation
content = re.sub(
    r'(<button className="px-8 py-4 bg-primary text-on-primary rounded-full font-label-lg text-label-lg shadow-xl shadow-primary/20 hover:shadow-primary/40 active:scale-95 transition-all flex items-center gap-2">)',
    r'<button onClick={() => window.location.href="/search"} className="px-8 py-4 bg-primary text-on-primary rounded-full font-label-lg text-label-lg shadow-xl shadow-primary/20 hover:shadow-primary/40 active:scale-95 transition-all flex items-center gap-2">',
    content
)

# View Specialist Network
content = re.sub(
    r'(<button className="px-8 py-4 glass-card rounded-full font-label-lg text-label-lg hover:bg-white/80 active:scale-95 transition-all">)',
    r'<button onClick={() => window.location.href="/search"} className="px-8 py-4 glass-card rounded-full font-label-lg text-label-lg hover:bg-white/80 active:scale-95 transition-all">',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating page.tsx links")

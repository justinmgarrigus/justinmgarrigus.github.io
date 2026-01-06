"""
Given a markdown document in stdin, converts it to an HTML page and outputs to 
stdout.
"""

import sys 
import re 
from datetime import datetime
import pytz 

# Read content from stdin.
try: 
    markdown = [line.strip() for line in sys.stdin.readlines()]
except EOFError: 
    print("Error: not enough lines in input markdown.")  
    sys.exit(1)

# Construct the output. 
html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="/style-content.css">
  </head>
  <body class="webpage">
    <script>
      fetch("config.json")
        .then(r => r.json())
        .then(cfg => {
          console.log("Here");
          var elements = document.getElementsByClassName("fullName");
          for (var i = 0; i < elements.length; i++) {
            elements[i].textContent = cfg.fullName;
          }
          elements = document.getElementsByClassName("firstName");
          console.log("Length = " + elements.length); 
          for (var i = 0; i < elements.length; i++) {
            console.log("Replaced."); 
            elements[i].textContent = cfg.firstName;
          } 
        }); 
    </script>
    <div class="main-content">
      <div class="main-section">
""" 

# Classify the markdown lines as either h4's, h3's, or paragraphs, and add them
# to the output. 
italic_reg = re.compile(r".*(\*[^\*]+\*).*")
bold_reg = re.compile(r".*(\*\*[^\*]+\*\*).*")
link_reg = re.compile(r".*(\[[^\]]+\])(\([^\)]+\)).*")
reading_table = False 
table_cols = None 
lines_written = 0 
for line in markdown:
    if len(line) == 0: 
        continue 

    # Substitute asterisks with italics.
    while mat := italic_reg.match(line):
        text = mat[1][1:-1]
        line = line[:mat.start(1)] + "<i>" + text + "</i>" + line[mat.end(1):]
   
    # Substitute double-asterisks with bolds.
    while mat := bold_reg.match(line):
        text = mat[1][2:-2] 
        line = line[:mat.start(1)] + "<b>" + text + "</b>" + line[mat.end(1):] 

    # Substitute links.
    while mat := link_reg.match(line): 
        text = mat[1][1:-1]
        link = mat[2][1:-1]
        target = (
            "_self" if link.startswith("/") and not link.endswith(".pdf")
            else "_parent"
        )
        line = (
            line[:mat.start(1)] 
            + f"<a href=\"{link}\" target=\"{target}\">{text}</a>"
            + line[mat.end(2):]
        )

    while "{{first_name}}" in line:
        line = line.replace("{{first_name}}", 
            "<span class=\"firstName\"></span>")
    while "{{full_name}}" in line:
        line = line.replace("{{full_name}}", 
            "<span class=\"fullName\"></span>")

    html += "        "
    
    if line.startswith("###"):
        line = line[3:].strip()
        line = "<h4>" + line + "</h4>"
        if reading_table:
            reading_table = False
            table_cols = None 
            html += "</table>" 
    elif line.startswith("##"):
        line = line[2:].strip()
        style = " style=\"padding-top: 10px;\"" if lines_written == 0 else ""
        line = f"<h3{style}>" + line + "</h3>"
        if reading_table:
            reading_table = False
            table_cols = None 
            html += "</table>" 
    elif line.startswith("|"):
        # Replace tables.
        if not reading_table: 
            reading_table = True
            table_cols = line.count("|")
            html += "<table>"
         
        assert line.count("|") == table_cols, f"Line: \"{line}\""
        html += "<tr>"
        for part in [p.strip() for p in line.split("|") if len(p) > 0]:
            html += "<td>" + part + "</td>" 
        html += "</tr>" 
        line = "" 

    else: 
        if reading_table:
            reading_table = False
            table_cols = None 
            html += "</table>" 

        line = "<p>" + line + "</p>"
    
    html += line + "\n"
    lines_written += 1 

timezone = pytz.timezone("US/Central") 
now = datetime.now(timezone) 
last_updated_time = now.strftime("%B %d, %Y at %-I:%M%p CST") 

# End with the last bunch of lines.
html += """
        <div class="last-updated"> 
          <p class="last-updated-text">
            Last updated %s
          </p>
        </div>

      </div> 
    </div>
  </body>
</html>
""" % last_updated_time

# Display it to stdout. 
print(html)

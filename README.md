# Comment Analysis
Using AI big models to analyze user comments, achieve tag classification and sentiment judgment.

# Overview
<a href="#install">Install</a>
<br>
<a href="#file">File</a>
<br>
<a href="#label">Label</a>
<br>
<a href="#ai">AI</a>
<br>
<a href="#run">Run</a>
<br>
<a href="#example">Example</a>
<br>

# Install

```bash
git clone https://github.com/xyjw/comment_analysis.git && cd comment_analysis
pip install -r requirements.txt
```

# File
Put the xlsx file in the data folder. XLSX files are used to save comment.
<br>
The column name of the comment must contain the keyword 'content'.
<br>
For Example
<br>
<br>
<img width="447" height="232" alt="image" src="https://github.com/user-attachments/assets/e2626027-09a2-41ba-bf3c-f2a5fe9a4454" />

# Label
Open label.txt to set labels. The data format of the tag is JSON.
<br>
For Example
<br>
<br>
<img width="483" height="378" alt="image" src="https://github.com/user-attachments/assets/379a9b64-3265-4c5a-960d-bdd6bfb89952" />

# AI
Open api.txt to set AI's apikey.
<br>
There is a certain amount of free credit available daily using <a href="https://openrouter.ai/">openrouter.ai</a>.
<br>
For Example
<br>
<br>
<img width="609" height="105" alt="image" src="https://github.com/user-attachments/assets/0e24991a-8a10-48c3-8dac-b159922bb237" />

# Run
```python
python main.py
```
# Example
<img width="869" height="284" alt="image" src="https://github.com/user-attachments/assets/a4df4909-989a-41ee-b6fa-3a921960c608" />
<br>
<br>
<img width="653" height="528" alt="image" src="https://github.com/user-attachments/assets/82303555-9cfe-494d-b49d-83a5a0917a61" />




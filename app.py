from flask import Flask, request
import requests
import os

app = Flask(__name__)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
CORP_ID = os.getenv('CORP_ID')
AGENT_ID = os.getenv('AGENT_ID')
AGENT_SECRET = os.getenv('AGENT_SECRET')

def get_access_token():
    try:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={AGENT_SECRET}"
        response = requests.get(url, timeout=10)
        return response.json().get('access_token')
    except:
        return None

def call_deepseek_api(question):
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}]
        }
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "AI正在思考中，请稍后再试..."
    except:
        return "AI服务暂时不可用"

def send_wechat_message(user_id, content):
    try:
        token = get_access_token()
        if not token:
            return False
            
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": int(AGENT_ID),
            "text": {"content": content[:2000]}
        }
        
        response = requests.post(url, json=data, timeout=10)
        return response.json().get('errcode') == 0
    except:
        return False

@app.route('/wechat', methods=['GET', 'POST'])
def handle_wechat():
    if request.method == 'GET':
        return request.args.get('echostr', '')
    
    try:
        data = request.get_json()
        user_id = data.get('FromUserName', '')
        content = data.get('Content', '').strip()
        
        if content:
            ai_response = call_deepseek_api(content)
            send_wechat_message(user_id, ai_response)
        
        return 'success'
    except:
        return 'success'

@app.route('/')
def home():
    return "AI机器人服务运行正常！"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
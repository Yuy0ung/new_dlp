import torch
from transformers import BertTokenizer, BertForSequenceClassification

# 模型和分词器的保存路径
model_save_path = "plugin\scan\model\models\malware_bert_model"

# 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(model_save_path)
model = BertForSequenceClassification.from_pretrained(model_save_path)

# 将模型移动到GPU（如果可用）
device = torch.device("cpu")
model.to(device)



def prepare_input(text, tokenizer, max_length=128):
    # 对输入文本进行编码
    inputs = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )

    # 将输入数据移动到GPU（如果可用）
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    return input_ids, attention_mask


def predict(text):
    # 准备输入数据
    input_ids, attention_mask = prepare_input(text, tokenizer)

    # 设置模型为评估模式
    model.eval()

    with torch.no_grad():
        # 获取模型输出
        outputs = model(input_ids, token_type_ids=None, attention_mask=attention_mask)
        logits = outputs.logits

    # 获取预测标签
    prediction = torch.argmax(logits, dim=-1).item()
#二值输出 0 1 int
    return prediction
#批量处理数据
def predict_all(text):
    # print(text)
    # 准备输入数据
    inputs=[]
    if not isinstance(text[0],list):
        text=[text[0]]
    else:
        text=text[0]
    for i in text:
        inputs+=[list(prepare_input(i, tokenizer))]
    # 设置模型为评估模式
    model.eval()

    with torch.no_grad():
        # 获取模型输出
        # print([torch.argmax(model(i[0], token_type_ids=None, attention_mask=i[1]).logits, dim=-1).item() for i in inputs],text)

        return any([torch.argmax(model(i[0], token_type_ids=None, attention_mask=i[1]).logits, dim=-1).item() for i in inputs])
#二值输出 0 1 int

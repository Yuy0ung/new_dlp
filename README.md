基于qfluentwidgets重建的DLP项目
TODO:

- [x] 重构代码
- [ ] 添加驱动白名单(ioctl)
- [ ] 被动扫描

TIPS:
如果安装requirements.txt后仍然存在如下报错

```
Traceback (most recent call last):
  File "C:\Users\Runwu2204\Desktop\new_dlp\view.py", line 12, in <module>
    from widgets.home import HomeWidget
  File "C:\Users\Runwu2204\Desktop\new_dlp\widgets\home.py", line 17, in <module>
    from plugin.scan.scan import ScanTask,TaskSignals
  File "C:\Users\Runwu2204\Desktop\new_dlp\plugin\scan\scan.py", line 6, in <module>
    from plugin.scan.preprocess.preprocess import start_preprocess
  File "C:\Users\Runwu2204\Desktop\new_dlp\plugin\scan\preprocess\preprocess.py", line 12, in <module>
    import magic
  File "C:\Users\Runwu2204\AppData\Local\Programs\Python\Python39\lib\site-packages\magic\__init__.py", line 209, in <module>
    libmagic = loader.load_lib()
  File "C:\Users\Runwu2204\AppData\Local\Programs\Python\Python39\lib\site-packages\magic\loader.py", line 49, in load_lib
    raise ImportError('failed to find libmagic.  Check your installation')
```

则需要

`pip uninstall python_magic_bin`

`pip install python-magic-bin==0.4.14 -i https://pypi.tuna.tsinghua.edu.cn/simple`

模型位置

model文件夹下

├── model.py
├── models
│   └── malware_bert_model
│       ├── config.json
│       ├── model.safetensors
│       ├── special_tokens_map.json
│       ├── tokenizer_config.json
│       └── vocab.txt
├── __pycache__
│   └── model.cpython-39.pyc
└── requirements.txt
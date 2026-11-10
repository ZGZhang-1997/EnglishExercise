# English Exercise

一个 Python 桌面英语学习软件。主界面提供两个练习模式：

- **Spoken** —— 预留入口，功能开发中。
- **Type Type** —— 打字练习：从 `books/` 文件夹选一本书，照着原文逐字输入，配合中文翻译与单词/句子朗读。

## 环境要求

- Python 3.10+（推荐 3.12）
- Windows（依赖 Windows 的语音与窗口 API）

## 运行

```bash
uv sync                      # 首次运行：创建 .venv、安装依赖并安装本项目
uv run english-exercise      # 启动主界面
```

也可以：

```bash
uv run python -m english_exercise
```

或双击 `run.bat`（使用 `.venv` 中的 pythonw 启动，不弹控制台）。

## 使用流程

1. 启动后进入主菜单，点 **Type Type**。
2. 弹出「选择一本书」窗口，列出 `books` 文件夹中的所有 `.txt` 书籍。
   - 点「打开 books 文件夹」可直接打开该目录，把书复制进去后点「刷新」。
   - 条目上显示文件大小和该书上次的练习进度。
   - 单击选中一本书，再点「开始练习」；双击条目也可直接开始。
3. 练习窗口中：上方是中文翻译，中间是原文（当前单词高亮），下方是输入行。
   - 打对前进，打错会退回当前单词开头并闪红。
   - 打完整句后自动循环朗读整句，播完按回车进入下一句。
   - 右上角「书架」按钮可随时保存进度并返回主菜单。
4. 进度按书籍分别保存，下次选中同一本书会从上次的句子继续。

## 配置

### API Key —— `keys.ini`（项目根目录）

所有服务的密钥集中放在项目根目录的 `keys.ini` 里，项目不引用任何项目文件夹之外的文件：

```ini
[deepl]
api_key = 你的 DeepL Key

[openai]          # 之后新增的服务照这样追加即可
api_key = sk-xxxx
```

- 键名可写 `api_key` / `key` / `token`，取第一个非空值。
- 环境变量 `<服务名>_API_KEY`（如 `DEEPL_API_KEY`）优先级更高，方便临时切换。
- 没有 `keys.ini` 时首次启动会自动生成一份模板；也可从 `keys.example.ini` 复制。
- `keys.ini` 含真实密钥，已在 `.gitignore` 中排除，请勿提交。
- 找不到 DeepL Key 时仍可练习，只是不显示中文翻译。

### 其他设置 —— `config.ini`（项目根目录）

```ini
[audio]
voice = en-US-AriaNeural
```

- `voice`：edge-tts 语音，可选值参考 [edge-tts 文档](https://github.com/rany2/edge-tts)。

### 全部文件都在项目内

`books/`、`config.ini`、`keys.ini` 以及运行时产生的 `data/`（进度、翻译缓存、音频缓存、
nltk 分词数据）都位于项目根目录，不依赖用户目录或桌面上的外部文件。
如需整体迁移，设置环境变量 `ENGLISH_EXERCISE_HOME` 指向新的根目录即可。

## 项目结构

采用 uv 标准的 `src` 布局，业务逻辑全部位于可安装包内：

```
├── pyproject.toml           # 项目元数据、依赖、入口点（english-exercise）
├── uv.lock                  # 锁定的依赖版本
├── .python-version          # Python 版本（uv 使用）
├── run.bat                  # 双击启动
├── config.ini               # 非敏感设置（音色等）
├── keys.ini                 # 各服务 API Key（不入库）
├── keys.example.ini         # keys.ini 模板
├── books/                   # 放 .txt 书籍（用户自行放入）
├── data/                    # 运行期数据：进度、缓存、音频、nltk 数据（自动生成）
├── src/english_exercise/
│   ├── __init__.py
│   ├── __main__.py           # 支持 python -m english_exercise
│   ├── main.py               # 入口：初始化环境并启动主菜单
│   ├── paths.py              # 根目录、books/data/config/keys 路径解析
│   ├── settings.py           # config.ini 与 keys.ini 读取
│   ├── theme.py              # 配色、字体、窗口小工具
│   ├── bookshelf.py          # 扫描书籍、记录上次选择
│   ├── progress.py           # 按书保存的练习进度
│   ├── text.py               # 书籍读取与分句
│   ├── translation.py        # DeepL 翻译与缓存
│   ├── audio.py              # 单词/整句音频生成与播放
│   └── ui/
│       ├── home.py           # 主菜单（Spoken / Type Type）
│       ├── book_picker.py    # 书目选择窗口
│       └── typing.py         # 打字练习窗口
└── tests/                    # pytest 单元测试
```

## 开发

```bash
uv run pytest        # 运行测试
uv run ruff check .  # 代码检查
```

## 依赖

| 包 | 用途 |
|---|---|
| customtkinter | GUI 界面 |
| pyttsx3 | 单词语音生成（wav） |
| edge-tts | 句子语音生成（mp3） |
| pygame | 音频播放 |
| deepl | DeepL 翻译 API |
| nltk | 英文分句 |

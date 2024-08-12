# Discord BotをPythonで実装
Discord Botで色々やるプロジェクト

### 現在できること
- /hey: こんにちはと言わせる <br>
- /createchannel: 複数のチャンネルをcsvファイルから読み込んで追加する

### 実装前の準備
1. Discord Botを作成する<br>
   以下参照<br>
   https://www.geeklibrary.jp/counter-attack/discord-js-bot/
2. BotのTokenを取得(後で使う)
### 実装の手順
1. プロジェクトをクローンする
    ```
    git clone https://github.com/Amos2610/discobot_python.git
    cd discobot_python
    ```
2. 環境ファイル(Bot Token)を編集する<br>
   .env.sampleファイルに自分で作成したBotのTokenを追加する<br>
   .env.sampleを.envに変更<br>
3. プログラムを実行する
   ```
   python bot.py
   ```<br>
4. Discord Botのいるのサーバで以下のコマンドを打つ<br>
   - /hey: こんにちはと言わせる
   - /createchannel: csvファイルからチャンネルを追加する
   
   

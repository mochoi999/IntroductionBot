import discord
from discord.ext import commands


class SelfIntroduction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("running now.")
        self.GUILD = self.bot.get_guild()  # メインサーバー
        self.DB_SERVER = self.bot.get_guild()  # データ管理用サーバー
        self.INTRODUCTION_CHANNEL = self.GUILD.get_channel()  #自己紹介チャンネル
        self.RULE_CHANNEL = self.GUILD.get_channel()  # ルールチャンネル

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        if not self.search_db_channel(member.id):  # 自己紹介データがない時
            await self.DB_SERVER.create_text_channel(name=member.name, topic=str(member.id))
            dm = await member.create_dm()
            await dm.send(embed=self.send_embed(
                "こんにちは！「SLものづくりサーバー」の案内スタッフ（bot）です。\nこの度は入鯖ありがとうございます。これからいくつか質問をします。\n"
                "回答内容が自己紹介として投稿されますので、回答をお願いします。\n回答を送信すると、次の質問に進みますのでお気をつけください。\nまず、お名前は何ですか？\n（※答えたくない場合は、 "
                "skip　と入力欄に打って送信してください。）"))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            if message.content == "/reset":
                return
            if self.search_db_channel(message.author.id):  # 自己紹介データがある場合
                channel = self.get_db_channel(message.author.id)
                count = len(await channel.history(limit=None).flatten())
                if count == 0:  # 名前を格納
                    await channel.send(message.content)
                    await message.channel.send(embed=self.send_embed("誰から招待を受けましたか？"))
                elif count == 1:  # 招待元を格納
                    await channel.send(message.content)
                    await message.channel.send(embed=self.send_embed("SLID（アバターのID）を教えてください。"))
                elif count == 2:  # SLIDを格納
                    await channel.send(message.content)
                    await message.channel.send(embed=self.send_embed("ものづくりの経験はありますか？\nある場合は、どんなことをどのくらいしたことがありますか？"))
                elif count == 3:  # ものづくりを格納
                    await channel.send(message.content)
                    await message.channel.send(embed=self.send_embed("これからどんなことをしてみたいですか？"))
                elif count == 4:  # してみたいことを格納
                    await channel.send(message.content)
                    await message.channel.send(embed=self.send_embed("一言お願いします。"))
                elif count == 5:  # 一言を格納
                    await channel.send(message.content)
                    await self.complete(channel, message)
                elif count == 7:  # 自己紹介が登録されている場合
                    await message.channel.send(embed=self.send_embed(f"{message.author.name}さんの自己紹介文は既に登録済みです。\n"
                                                                     f"変更する場合は、 `/reset` コマンドを送信して下さい"))
            else:  # 自己紹介データが無い場合
                if message.author in self.GUILD.members:
                    await self.DB_SERVER.create_text_channel(name=message.author.name, topic=message.author.id)
                    await message.channel.send(embed=self.send_embed("自己紹介文が見つかりませんでした。\n質問に答えると自己紹介が登録できます。"))
                    await message.channel.send(embed=self.send_embed("名前を入力してください"))
                else:
                    await message.channel.send(embed=self.send_embed("専用サーバーに参加していないと自己紹介を登録する事が出来ません。"))

    # DBサーバーからメンバーの有無を調べる
    # 有 True : 無 False
    def search_db_channel(self, _id):
        channels = self.DB_SERVER.text_channels
        channel_topics = list(map(lambda c: c.topic, channels))
        if str(_id) in channel_topics:
            return True
        else:
            return False

    def get_db_channel(self, _id):
        for channel in self.DB_SERVER.text_channels:
            if channel.topic == str(_id):
                return channel

    def send_embed(self, msg):
        return discord.Embed(description=msg)

    # ---全ての質問に答えたときに呼び出される---
    async def complete(self, channel, message):
        # 格納されたメッセージをすべて取得
        messages = await channel.history(limit=None).flatten()
        # embedにして整形
        embed = self.embed_generator(self.adjust(messages), message.author)
        # 完成した自己紹介文の最終チェック(修正が可能)
        embed_message = await message.channel.send(embed=embed)
        await message.channel.send(embed=self.send_embed("この内容で自己紹介を登録しますか？\nOKなら👍リアクションを、修正する場合は❌リアクションを押して下さい"))
        # リアクションを追加
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("❌")
        # 押されたemojiを取得
        emoji = await self.wait_reaction_add(channel, embed_message)
        # 押された絵文字が👍の時(今の内容で登録する)
        if emoji == "👍":
            register_msg = await self.INTRODUCTION_CHANNEL.send(embed=embed)
            await channel.send(register_msg.id)
            await message.channel.send(
                f"終了です。ありがとうございました。\n自己紹介をサーバーに投稿しました。\n最後に、 {self.RULE_CHANNEL.mention} "
                "をお読みください。（リンクをクリックしてください）\nでは、楽しいサーバーライフを！")
        # 押された絵文字が❌の時(内容を変更する)
        elif emoji == "❌":
            await message.channel.send(embed=self.send_embed("内容をリセットします"))
            # TextChannelを再度作成し直し、リセットする
            await channel.delete()
            await self.DB_SERVER.create_text_channel(name=message.author.name, topic=message.author.id)
            await message.channel.send(embed=self.send_embed("名前を入力してください"))

    # ---completeメソッド内でのみ呼び出される---
    # Embedオブジェクトを作成するメソッド
    # 質問内容を追加する場合は、ここを弄る
    def embed_generator(self, _list, member):
        embed = discord.Embed(title="自己紹介")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"【 __名前__ 】", value=f"  {_list[0]}", inline=False)
        embed.add_field(name=f"【__招待元__】", value=f"  {_list[1]}", inline=False)
        embed.add_field(name=f"【 __SLID__ 】", value=f"  {_list[2]}", inline=False)
        if _list[3] != "skip":
            embed.add_field(name=f"【 __ものづくり経験__ 】", value=f"  {_list[3]}", inline=False)
        if _list[4] != "skip":
            embed.add_field(name=f"【 __してみたいこと__ 】", value=f"  {_list[4]}", inline=False)
        embed.add_field(name=f"【 __一言__ 】", value=f"  {_list[5]}", inline=False)
        return embed

    # ---completeメソッド内でのみ呼び出される---
    # channel内のメッセージlistの並びを逆にし、disocrd.Messageオブジェクトじゃなくdiscord.Message.Contentを格納
    def adjust(self, messages):
        messages.reverse()
        return list(map(lambda ms: ms.content, messages))

    # ---completeメソッド内でのみ呼び出される---
    # リアクションが押されたら、そのリアクションをreturnする
    async def wait_reaction_add(self, channel, message):
        # リアクションを押したユーザーがbotじゃなく、押された絵文字が👍か❌であり、リアクションを押したメッセージのidが送信されたembedメッセージのidと同じで、リアクションを押したユーザーのidとDEBUGサーバー内のchannel名が一致した場合のみ、処理が走る
        def check(reaction, user):
            return not user.bot and reaction.emoji in ("❌", "👍") and reaction.message.id == message.id and\
                   str(user.id) == channel.topic

        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        # リアクションが押されたら、押されたリアクションをreturnする
        if reaction.emoji == "👍" or reaction.emoji == "❌":
            return reaction.emoji

    @commands.command()
    async def reset(self, ctx):
        if ctx.author.bot:
            return
        if isinstance(ctx.channel, discord.DMChannel):
            if self.search_db_channel(ctx.author.id):  # 自己紹介データが存在する場合
                await ctx.send(embed=self.send_embed("自己紹介文を再登録します。"))
                channel = self.get_db_channel(ctx.author.id)
                count = len(await channel.history(limit=None).flatten())
                if count == 7:
                    msg_id = channel.last_message.content
                    msg = await self.INTRODUCTION_CHANNEL.fetch_message(int(msg_id))
                    await msg.delete()
                await channel.delete()
                await self.DB_SERVER.create_text_channel(name=ctx.author.name, topic=ctx.author.id)
                await ctx.channel.send(embed=self.send_embed("名前を入力してください"))

            else:  # 自己紹介データが存在しない場合
                await ctx.channel.send(embed=self.send_embed("自己紹介データがないので`reset`を実行できませんでした"))


def setup(bot):
    return bot.add_cog(SelfIntroduction(bot))

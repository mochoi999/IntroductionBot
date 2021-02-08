from discord.ext import commands
import discord
import asyncio
import requests

class SelfIntroduction(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.GUILD_ID = 698499861942894683 #サーバーid
        self.INTRODUCTION_CHANNEL_ID = 698504607428509806 #サーバー内の自己紹介チャンネルID
        self.DEBUG_GUILD_ID = 808202985573711883 #DEBUGサーバーのID ※変更しないようにお願いします。

    #Botを起動したときに__init__に格納したIDからオブジェクトを取得
    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")
        self.GUILD = self.bot.get_guild(self.GUILD_ID)
        self.INTRODUCTION_CHANNEL = self.GUILD.get_channel(self.INTRODUCTION_CHANNEL_ID)
        self.DEBUG_GUILD = self.bot.get_guild(self.DEBUG_GUILD_ID)

    #サーバーにメンバーが参加した時
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        for channel in self.DEBUG_GUILD.text_channels:
            #DEBUGサーバーからServer参加者のidと同じ名前のTextChannelを見つける
            if channel.name == str(member.id):
                return
        else:
            #discord.DMChannelオブジェクトを取得
            dm = await member.create_dm()
            #参加したメンバーのidを名前にしたTextChannelを作成
            await self.DEBUG_GUILD.create_text_channel(str(member.id))
            #参加者にdmを送る
            await dm.send(embed=self.send_embed("こんにちは！「SLものづくりサーバー」の案内スタッフ（bot）です。\nこの度は入鯖ありがとうございます。これからいくつか質問をします。\n回答内容が自己紹介として投稿されますので、回答をお願いします。\n回答を送信すると、次の質問に進みますのでお気をつけください。\nまず、お名前は何ですか？\n（※答えたくない場合は、 skip　と入力欄に打って送信してください。）"))

    #DMチャンネルにメッセージが送られた時
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            #送信者がbotの場合は無視する
            if message.author.bot:
                return
            for channel in self.DEBUG_GUILD.text_channels:
                #DEBUGサーバーからメッセージ送信者のidと同じ名前のTextChannelを見つける
                if channel.name == str(message.author.id):
                    #channelを見つけたらそのチャンネル内の合計メッセージ数を取得する
                    count = await self.get_count(channel)

                    #channel内のメッセージ数が6じゃなく、¥editコマンドが送信された時の処理
                    if count != 6 and message.content.startswith("/edit"):
                        await message.channel.send(embed=self.send_embed("自己紹介を登録してから/editコマンドを使用して下さい。"))
                        break
                    #メッセージ数が0の時の処理(名前が格納される)
                    if count == 0:
                        await self.send_message(channel, message, "SLID（アバターのID）を教えてください。")
                        break
                    #メッセージ数が1の時(SLIDが格納される)
                    elif count == 1:
                        await self.send_message(channel, message, "ものづくりの経験はありますか？\nある場合は、どんなことをどのくらいしたことがありますか？")
                        break
                    #メッセージ数が2の時(ものづくり経験が格納される)
                    elif count == 2:
                        await self.send_message(channel, message, "これからどんなことをしてみたいですか？")
                        break
                    #メッセージ数が3の時(してみたいことが格納される)
                    elif count == 3:
                        await self.send_message(channel, message, "一言お願いします。")
                        break
                    #メッセージ数が4の時(これから勉強していきたいことが格納される)
                    elif count == 4:
                        await self.send_message(channel, message, "これで質問は終了です")
                        await self.complete(channel, message)
                        break

                    #メッセージ数が6かつ¥editコマンドを送信した場合の処理
                    elif count == 6 and message.content.startswith("/edit"):
                        await message.channel.send(embed=self.send_embed("自己紹介文を再登録します。"))
                        #channel内の一番下のメッセージ(自己紹介に送られたembedメッセージid)を取得する
                        msg = await channel.history(limit=None).flatten()
                        #メッセージidからdiscord.Messageオブジェクトを取得する
                        msg = await self.INTRODUCTION_CHANNEL.fetch_message(int(msg[0].content))
                        #前の自己紹介文を削除する
                        await msg.delete()
                        #DEBUGサーバーのchannelも削除する
                        await channel.delete()
                        #新しくコマンド送信者のidと同じ名前のTextChannelを作成する
                        await self.DEBUG_GUILD.create_text_channel(str(message.author.id))
                        await message.channel.send(embed=self.send_embed("名前を入力してください"))
                        break
                    #メッセージ数が6の時
                    elif count == 6:
                        await message.channel.send(embed=self.send_embed(f"{message.author.name}さんの自己紹介文は既に登録済みです。\n変更する場合は、/editコマンドを送信して下さい"))
                        break
            #DEBUGサーバー内にメッセージ送信者のチャンネルが見つからなかったときに、TextChanenlを作成する
            else:
                await self.DEBUG_GUILD.create_text_channel(str(message.author.id))
                await message.channel.send(embed=self.send_embed("自己紹介文が見つかりませんでした。\n質問に答えると自己紹介が登録できます。"))
                await message.channel.send(embed=self.send_embed("名前を入力してください"))

    #---on_messageイベント内でのみ呼び出される---
    #channelとdmにメッセージを送信するメソッド
    async def send_message(self, channel, message, content):
        await channel.send(message.content)
        await message.channel.send(embed=self.send_embed(content))

    def send_embed(self, msg):
        return discord.Embed(description=msg)

    #---on_messageイベント内でのみ呼び出される---
    #チャンネル内のメッセージ総数を取得し、returnする
    async def get_count(self, channel):
        count = await channel.history(limit=None).flatten()
        return len(count)

    #---全ての質問に答えたときに呼び出される---
    async def complete(self, channel, message):
        #格納されたメッセージをすべて取得
        messages = await channel.history(limit=None).flatten()
        #embedにして整形
        embed = self.embed_generator(self.adjust(messages), message.author)
        #完成した自己紹介文の最終チェック(修正が可能)
        embed_message = await message.channel.send(embed=embed)
        await message.channel.send(embed=self.send_embed("この内容で自己紹介を登録しますか？\nOKなら👍リアクションを、修正する場合は❌リアクションを押して下さい"))
        #リアクションを追加
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("❌")
        #押されたemojiを取得
        emoji = await self.wait_reaction_add(channel, embed_message)
        #押された絵文字が👍の時(今の内容で登録する)
        if emoji == "👍":
            register_msg = await self.INTRODUCTION_CHANNEL.send(embed=embed)
            await channel.send(register_msg.id)
            await message.channel.send("終了です。ありがとうございました。\n自己紹介をサーバーに投稿しました。\n最後に、 <#808237191037321326> をお読みください。（リンクをクリックしてください）\nでは、楽しいサーバーライフを！")
        #押された絵文字が❌の時(内容を変更する)
        elif emoji == "❌":
            await message.channel.send(embed=self.send_embed("内容をリセットします"))
            #TextChannelを再度作成し直し、リセットする
            await channel.delete()
            await self.DEBUG_GUILD.create_text_channel(message.author.id)
            await message.channel.send(embed=self.send_embed("名前を入力してください"))

    #---completeメソッド内でのみ呼び出される---
    #Embedオブジェクトを作成するメソッド
    #質問内容を追加する場合は、ここを弄る
    def embed_generator(self, list, member):
        embed = discord.Embed(title="自己紹介")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"【 __名前__ 】", value=f"  {list[0]}", inline=False)
        embed.add_field(name=f"【 __SLID__ 】", value=f"  {list[1]}", inline=False)
        if list[2] == "skip":
            pass
        else:
            embed.add_field(name=f"【 __ものづくり経験__ 】", value=f"  {list[2]}", inline=False)
        if list[3] == "skip":
            pass
        else:
            embed.add_field(name=f"【 __してみたいこと__ 】", value=f"  {list[3]}", inline=False)
        embed.add_field(name=f"【 __一言__ 】", value=f"  {list[4]}", inline=False)
        return embed

    #---completeメソッド内でのみ呼び出される---
    #channel内のメッセージlistの並びを逆にし、disocrd.Messageオブジェクトじゃなくdiscord.Message.Contentを格納
    def adjust(self, messages):
        messages.reverse()
        return list(map(lambda messages: messages.content, messages))

    #---completeメソッド内でのみ呼び出される---
    #リアクションが押されたら、そのリアクションをreturnする
    async def wait_reaction_add(self, channel, message):
        #リアクションを押したユーザーがbotじゃなく、押された絵文字が👍か❌であり、リアクションを押したメッセージのidが送信されたembedメッセージのidと同じで、リアクションを押したユーザーのidとDEBUGサーバー内のchannel名が一致した場合のみ、処理が走る
        def check(reaction,user):
            return user.bot == False and reaction.emoji == "👍" and reaction.message.id == message.id and str(user.id) == channel.name or user.bot == False and reaction.emoji == "❌" and reaction.message.id == message.id and str(user.id) == channel.name
        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        #リアクションが押されたら、押されたリアクションをreturnする
        if reaction.emoji == "👍" or reaction.emoji == "❌":
            return reaction.emoji

def setup(bot):
    return bot.add_cog(SelfIntroduction(bot))
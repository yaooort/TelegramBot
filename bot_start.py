import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import random

# 是否开启图灵机器人聊天
is_open_bot_simple = False


def hello(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(chat_id=update.message.chat_id, text="我是抽烟群的小秘书，有事请找我说。。。您可以输入 /抽烟 /开启机器人  /关闭机器人 指令")


def som(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(chat_id=update.message.chat_id, text="客官，请输入您想设定的抽烟时间,格式请参考 '/抽烟时间 12:30'")


def remove(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    remove_job()
    bot.send_message(chat_id=update.message.chat_id, text="客官，所有定时任务均已经删除。")


def open_bot(bot, update):
    """
    /开启机器人 命令
    :param bot:
    :param update:
    :return:
    """
    global is_open_bot_simple
    is_open_bot_simple = True
    bot.send_message(chat_id=update.message.chat_id, text="各位，我会回复各位的任何问题！有问题都可以问我，讲笑话，唐诗宋词无所不能，哈哈哈!")


def close_bot(bot, update):
    """
    /关闭机器人 命令
    :param bot:
    :param update:
    :return:
    """
    global is_open_bot_simple
    is_open_bot_simple = False
    bot.send_message(chat_id=update.message.chat_id, text="各位，我走了!")


def som_time(bot, update):
    """
       所有消息的过滤
       :param bot:
       :param update:
       :return:
       """
    message = update.message.text
    new = message.replace("/抽烟时间", "")
    new = new.strip()
    if new.isdigit() and 0 <= int(new) < 23:
        # 纯数字的结尾，就当
        h = int(new)
        add_scheduler(chat_id=update.message.chat_id, h=h, m=0)
        bot.send_message(chat_id=update.message.chat_id, text='温馨提示!成功添加抽烟时间!')
        bot.send_message(chat_id=update.message.chat_id,
                         text='我将提醒各位客官老爷们 每个工作日的' + new + '点抽烟,请勿重复添加。如果需要删除提醒请输入 /remove')
    elif ':' in new:
        time = new.split(':')
        if len(time) == 2 and 0 <= int(time[0]) < 23 and 0 <= int(time[1]) < 60:
            add_scheduler(chat_id=update.message.chat_id, h=int(time[0]), m=int(time[1]))
            bot.send_message(chat_id=update.message.chat_id, text='温馨提示!成功添加抽烟时间!')
            bot.send_message(chat_id=update.message.chat_id,
                             text='我将提醒各位客官老爷们 每个工作日的' + new + '分抽烟,请勿重复添加。如果需要删除提醒请输入 /remove')
    elif '：' in new:
        time = new.split('：')
        if len(time) == 2 and 0 <= int(time[0]) < 23 and 0 <= int(time[1]) < 60:
            add_scheduler(chat_id=update.message.chat_id, h=int(time[0]), m=int(time[1]))
            bot.send_message(chat_id=update.message.chat_id, text='温馨提示!成功添加抽烟时间!')
            bot.send_message(chat_id=update.message.chat_id,
                             text='我将提醒各位客官老爷们 每个工作日的' + new + '分抽烟,请勿重复添加。如果需要删除提醒请输入 /remove')


def echo(bot, update):
    """
    所有消息的过滤
    :param bot:
    :param update:
    :return:
    """

    msg = update.message.text
    print(msg)
    if '对不' in msg:
        call_message = '你说的对!'
    elif '走不' in msg:
        call_message = '说走就走'
    elif '是不' in msg:
        call_message = '是的'
    elif '好不' in msg:
        call_message = '好'
    elif '慌不' in msg or '芳不' in msg:
        call_message = '有点小芳'
    elif '去不' in msg:
        call_message = '21点走起!再不去就没饭吃了'
    else:
        if is_open_bot_simple:
            call_message = ask_bot(msg)
        else:
            return
    bot.send_message(chat_id=update.message.chat_id, text=call_message)


def caps(bot, update, args):
    """
    内联查询 @caps 需要查询的内容
    :param bot:
    :param update:
    :param args:
    :return:
    """
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    """
    处理内联的查询关键字
    :param bot:
    :param update:
    :return:
    """
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def unknown(bot, update):
    """
    未知命令
    :param bot:
    :param update:
    :return:
    """
    # if is_open_bot_simple:
    bot.send_message(chat_id=update.message.chat_id, text='这个指令我不明白')
    # else:
    # bot.send_message(chat_id=update.message.chat_id, text=ask_bot(update.message.text))


updater = Updater('737719054:AAH2SwsM8zFbU_MhSP-9LYydxB68AhHg0T4')

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

start_handler = CommandHandler('hello', hello)
dispatcher.add_handler(start_handler)

som_handler = CommandHandler('抽烟', som)
dispatcher.add_handler(som_handler)

som_time_handler = CommandHandler('抽烟时间', som_time)
dispatcher.add_handler(som_time_handler)

dispatcher.add_handler(CommandHandler('remove', remove))

dispatcher.add_handler(CommandHandler('开启机器人', open_bot))

dispatcher.add_handler(CommandHandler('关闭机器人', close_bot))

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)

inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)
# 监听
updater.start_polling()
# 创建定时任务
scheduler = BackgroundScheduler()


def add_scheduler(chat_id, h, m):
    """
    添加周内任务
    :param h:
    :param m:
    :return:
    """
    # 在每年 每月份中的每个星期的工作日中的 00:00, 01:00, 02:00 和 03:00 执行 job_func 任务
    scheduler.add_job(job_func, 'cron', day_of_week='mon,tue,wed,thu,fri', hour=h, minute=m,
                      timezone='Asia/Shanghai', args=[chat_id])


def remove_job():
    scheduler.remove_all_jobs()


def job_func(chat_id):
    """
    定时方法
    :return:
    """
    updater.bot.sendMessage(chat_id=chat_id,
                            text='各位赌徒,下去散散心!')


# 启动定时器
scheduler.start()


# noinspection PyBroadException
def ask_bot(question):
    if len(question) > 127:
        return
    data_map = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": question
            }
        },
        "userInfo": {
            "apiKey": "7695c949f5504b90a26e7906ce118f27",
            "userId": str(random.randint(10000, 100000))
        }
    }
    try:
        # 测试请求
        print(requests.get('https://api.github.com/events').text)
        print('开始请求')
        response = requests.post('http://openapi.tuling123.com/openapi/api/v2', json=data_map).json()
        print(response)
        code = response['intent']['code']
        if code == 10004:
            re_str = response['results'][0]['values']['text']
            print(re_str)
            return re_str
        else:
            return '狗日的，脑子坏了！'
    except Exception as w:
        return '狗日的，脑子坏了！'

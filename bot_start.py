from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging
from apscheduler.schedulers.background import BackgroundScheduler


def hello(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(chat_id=update.message.chat_id, text="我是抽烟群的小秘书，有事请找我说。。。您可以输入 /抽烟 ")


def som(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    bot.send_message(chat_id=update.message.chat_id, text="客官，请输入您想设定的抽烟时间,格式请参考 '>抽烟时间12:30'")


def remove(bot, update):
    """
    /start 命令
    :param bot:
    :param update:
    :return:
    """
    remove_job()
    bot.send_message(chat_id=update.message.chat_id, text="客官，所有定时任务均已经删除。")


def echo(bot, update):
    """
    所有消息的过滤
    :param bot:
    :param update:
    :return:
    """
    message = update.message.text
    if message.startswith('>抽烟时间'):
        new = message.replace(">抽烟时间", "")
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
    bot.send_message(chat_id=update.message.chat_id, text="我不明白这个命令")


updater = Updater('737719054:AAH2SwsM8zFbU_MhSP-9LYydxB68AhHg0T4')

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

start_handler = CommandHandler('hello', hello)
dispatcher.add_handler(start_handler)

som_handler = CommandHandler('抽烟', som)
dispatcher.add_handler(som_handler)

dispatcher.add_handler(CommandHandler('remove', remove))

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
                            text='各位客官老爷们,抽烟时间到了!')


# 启动定时器
scheduler.start()

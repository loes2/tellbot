import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# وضع التوكن الخاص بالبوت هنا
TOKEN = '7838191538:AAHm79xzV1IlEu5NI-L25majcR_o1EGS49Y'
# تخزين الأعضاء المكتمين
muted_users = set()

# أمر كتم العضو
async def mute(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    # التحقق مما إذا كان هناك معامل (ID أو Username)
    if len(context.args) == 0:
        # إذا لم يكن هناك معامل، نحتاج للرد على عضو
        user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if user:
            # إضافة المستخدم إلى قائمة المكتمين
            muted_users.add(user.id)
            await update.message.reply_text(f"تم كتم {user.first_name}.")
            # كتم العضو في القروب
            await context.bot.restrict_chat_member(chat_id, user.id, can_send_messages=False)
        else:
            await update.message.reply_text("الرجاء الرد على رسالة عضو لتكتمه.")
    else:
        # إذا كان هناك معامل، يمكننا كتم العضو باستخدام ID أو Username
        target = context.args[0]
        user = None
        if target.isdigit():  # إذا كان المعامل هو ID
            user = await update.message.chat.get_member(int(target))
        else:  # إذا كان المعامل هو Username
            user = await update.message.chat.get_member(target)
        
        if user:
            muted_users.add(user.id)
            await update.message.reply_text(f"تم كتم {user.first_name} ({user.username if user.username else 'لا يوجد اسم مستخدم'}).")
            await context.bot.restrict_chat_member(chat_id, user.id, can_send_messages=False)
        else:
            await update.message.reply_text(f"لم يتم العثور على العضو {target}.")

# أمر إلغاء كتم العضو
async def unmute(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if len(context.args) == 0:
        # إذا لم يكن هناك معامل، نحتاج للرد على عضو
        user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if user:
            if user.id in muted_users:
                # إزالة العضو من قائمة المكتمين
                muted_users.remove(user.id)
                await update.message.reply_text(f"تم إلغاء كتم {user.first_name}.")
                await context.bot.restrict_chat_member(chat_id, user.id, can_send_messages=True)
            else:
                await update.message.reply_text(f"{user.first_name} ليس مكتمًا.")
        else:
            await update.message.reply_text("الرجاء الرد على رسالة عضو لإلغاء كتمه.")
    else:
        # إذا كان هناك معامل، يمكننا إلغاء كتم العضو باستخدام ID أو Username
        target = context.args[0]
        user = None
        if target.isdigit():  # إذا كان المعامل هو ID
            user = await update.message.chat.get_member(int(target))
        else:  # إذا كان المعامل هو Username
            user = await update.message.chat.get_member(target)
        
        if user:
            if user.id in muted_users:
                muted_users.remove(user.id)
                await update.message.reply_text(f"تم إلغاء كتم {user.first_name} ({user.username if user.username else 'لا يوجد اسم مستخدم'}).")
                await context.bot.restrict_chat_member(chat_id, user.id, can_send_messages=True)
            else:
                await update.message.reply_text(f"{user.first_name} ليس مكتمًا.")
        else:
            await update.message.reply_text(f"لم يتم العثور على العضو {target}.")

# أمر لحذف الرسائل من المكتمين
async def delete_muted_messages(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.id in muted_users:
        # حذف الرسالة إذا كان العضو مكتمًا
        await update.message.delete()

async def main():
    # إعداد البوت
    application = Application.builder().token(TOKEN).build()

    # إضافة أوامر البوت
    application.add_handler(CommandHandler('mute', mute, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler('unmute', unmute, filters=filters.ChatType.GROUPS))

    # حذف الرسائل من المكتمين
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_muted_messages))

    # بدء البوت
    await application.run_polling()

# تشغيل البوت باستخدام create_task لتجنب الخطأ في حالة وجود حدث قيد التشغيل
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # استخدام create_task بدلاً من run()
    loop.run_forever()  # بدء حلقة الحدث إذا كانت غير مفعلة

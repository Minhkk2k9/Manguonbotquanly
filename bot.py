import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

# **🔹 CẤU HÌNH BOT**
API_TOKEN = "7550142487:AAGKx3gjePiHbnYYA7_Rrg-ssJFokHRcMWg"
bot = telebot.TeleBot(API_TOKEN)

# **🔹 DANH SÁCH QUẢN TRỊ**
ALLOWED_USERS = {5909176384, 6839646737, 5981823480, 6956722046}
ALLOWED_CHATS = {-1002529918676, -1002304692212}

# **🔹 KIỂM TRA QUYỀN SỬ DỤNG**
def is_allowed(message):
    return (message.from_user.id in ALLOWED_USERS) or (message.chat.id in ALLOWED_CHATS)

# **🔹 XỬ LÝ LỆNH CẦN TRẢ LỜI TIN NHẮN**
def get_reply_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Vui lòng trả lời tin nhắn của người cần áp dụng lệnh.")
        return None
    return message.reply_to_message.from_user.id, message.reply_to_message.from_user.username

# **🔹 THĂNG CẤP QUẢN TRỊ (KHÔNG THỂ THAY ĐỔI THÔNG TIN NHÓM)**
@bot.message_handler(commands=['thangcap'])
def promote_user(message):
    if not is_allowed(message):
        return

    user_id, username = get_reply_user(message)
    if user_id is None:
        return

    bot.promote_chat_member(
        chat_id=message.chat.id,
        user_id=user_id,
        can_change_info=False,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=False
    )
    bot.reply_to(message, f"✅ **{username} đã được thăng cấp thành quản trị viên!**")

# **🔹 HẠ CẤP QUẢN TRỊ**
@bot.message_handler(commands=['hacap'])
def demote_user(message):
    if not is_allowed(message):
        return

    user_id, username = get_reply_user(message)
    if user_id is None:
        return

    bot.promote_chat_member(
        chat_id=message.chat.id,
        user_id=user_id,
        can_change_info=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False
    )
    bot.reply_to(message, f"⏬ **{username} đã bị hạ cấp!**")

# **🔹 KHOÁ CHAT (MẶC ĐỊNH VĨNH VIỄN NẾU KHÔNG CÓ THỜI GIAN)**
@bot.message_handler(commands=['câm'])
def mute_user(message):
    if not is_allowed(message):
        return

    user_id, username = get_reply_user(message)
    if user_id is None:
        return

    args = message.text.split()
    mute_time = None
    if len(args) > 1:
        try:
            mute_time = int(args[1])
        except ValueError:
            bot.reply_to(message, "❌ Vui lòng nhập thời gian khoá (phút) hoặc để trống để khoá vĩnh viễn.")

    until_date = datetime.now() + timedelta(minutes=mute_time) if mute_time else None
    bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False, until_date=until_date)
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🛑 Mở khoá mõm", callback_data=f"unmute_{user_id}"))

    bot.reply_to(message, f"🔇 **{username} đã bị câm {'trong ' + str(mute_time) + ' phút' if mute_time else 'vĩnh viễn'}**", reply_markup=keyboard)

# **🔹 BAN THÀNH VIÊN & XOÁ TOÀN BỘ TIN NHẮN**
@bot.message_handler(commands=['cút'])
def ban_user(message):
    if not is_allowed(message):
        return

    user_id, username = get_reply_user(message)
    if user_id is None:
        return

    bot.ban_chat_member(message.chat.id, user_id)
    bot.delete_message(message.chat.id, message.reply_to_message.message_id)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🚪 Mở ban", callback_data=f"unban_{user_id}"))

    bot.reply_to(message, f"🚫 **{username} đã bị cút khỏi nhóm vĩnh viễn!**", reply_markup=keyboard)

# **🔹 XỬ LÝ NÚT MỞ KHOÁ**
@bot.callback_query_handler(func=lambda call: call.data.startswith("unmute_") or call.data.startswith("unban_"))
def handle_callback(call):
    if call.from_user.id not in ALLOWED_USERS:
        bot.answer_callback_query(call.id, "❌ Bạn không có quyền thực hiện thao tác này!", show_alert=True)
        return

    user_id = int(call.data.split("_")[1])
    if call.data.startswith("unmute_"):
        bot.restrict_chat_member(call.message.chat.id, user_id, can_send_messages=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ **Đã mở khoá mõm cho {user_id}!**")
    elif call.data.startswith("unban_"):
        bot.unban_chat_member(call.message.chat.id, user_id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ **Đã cho {user_id} vào lại!**")

# **🔹 CHẠY BOT**
print("🤖 Bot đang chạy...")
bot.infinity_polling()

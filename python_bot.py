from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

from movie_converter import convert_mov_to_mp4

import os


TOKEN = '' # eg. Needed to change
BOT_USERNAME: Final = '' # eg. Needed to change

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am banana!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a banana! Please type something so I can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is custom command!')

# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed:
        return 'Hey There'
    
    if 'how are you' in processed:
        return 'I am good!'
    
    if 'i love python' in processed:
        return 'Remember to subcribe!'
    
    return 'I do not understand what you wrote...'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)            
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot: ', response)
    await update.message.reply_text(response)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.video:
        video = update.message.video
        file_id = video.file_id

        # Get the file
        file = await context.bot.get_file(file_id)

        # Download the file
        video_file_name = video.file_name or "user_uploaded_video.mp4"
        download_path = f"./downloads/{video_file_name}"
        converted_path = f"./exports/{video_file_name}"
        await file.download_to_drive(download_path)

        # Respond to the user
        await update.message.reply_text(f"Video '{video_file_name}' downloaded successfully!")

        try:
            convert_mov_to_mp4(download_path, converted_path)
            await update.message.reply_text(f"Video converted successfully: {converted_path}")
        except Exception as e:
            await update.message.reply_text(f"Video conversion failed: {str(e)}")
        finally:
            # Optional: Clean up the original file
            if os.path.exists(download_path):
                os.remove(download_path)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.document:
        document = update.message.document
        file_id = document.file_id

        # Get the file
        file = await context.bot.get_file(file_id)

        # Download the file
        original_file_name = document.file_name or "user_uploaded_file.mov"
        file_base_name, file_extension = os.path.splitext(original_file_name)
        file_extension = file_extension.lower()  
        download_path = f"./downloads/{original_file_name}"
        await file.download_to_drive(download_path)

        # Check file type and extension
        if file_extension == ".mp4":
            await update.message.reply_text(f"File is already in .mp4 format: {original_file_name}")
        elif file_extension == ".mov":
            # Convert the .mov file to .mp4
            converted_file_name = f"{file_base_name}.mp4"
            converted_file_path = f"./exports/{converted_file_name}"
            try:
                convert_mov_to_mp4(download_path, converted_file_path)
                await update.message.reply_text(f"File converted successfully: {converted_file_name}")

                # Upload the converted file back to the user
                with open(converted_file_path, "rb") as converted_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=converted_file,
                        filename=converted_file_name,
                        caption="Here is your converted file!"
                    )
            except Exception as e:
                await update.message.reply_text(f"File conversion failed: {str(e)}")
            # finally:
            #     # Optional: Clean up the original file
            #     if os.path.exists(download_path):
            #         os.remove(download_path)
        else:
            await update.message.reply_text("Unsupported file type. Please upload a .mov or .mp4 file.")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Video messages
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
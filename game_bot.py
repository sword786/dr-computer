import itertools
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Function to generate combinations and totals
def generate_combinations(numbers):
    results = set()
    combinations_dict = {}

    # Generate all possible permutations of the numbers (without repetition)
    for perm in itertools.permutations(numbers):
        for operators in itertools.product(['+', '-', '*', '/'], repeat=3):
            # Generate the expression with and without parentheses
            expr_no_paren = f"{perm[0]} {operators[0]} {perm[1]} {operators[1]} {perm[2]} {operators[2]} {perm[3]}"
            expr_with_paren = f"({perm[0]} {operators[0]} {perm[1]}) {operators[1]} ({perm[2]} {operators[2]} {perm[3]})"
            
            # Try evaluating both expressions
            for expr in [expr_no_paren, expr_with_paren]:
                try:
                    # Evaluate the result
                    result = eval(expr)
                    
                    # Check if the result is within the desired range and is an integer
                    if 10 < result < 100 and isinstance(result, int):
                        # Only store the first combination for each total
                        if result not in combinations_dict:
                            combinations_dict[result] = expr
                            results.add(result)
                except ZeroDivisionError:
                    continue
    
    return combinations_dict

# Command handler to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send me four numbers separated by spaces, and I'll show you the possible totals and combinations.")

# Command handler to process numbers and show results
async def process_numbers(update: Update, context: CallbackContext):
    # Get the user input (numbers) and process it
    user_input = update.message.text
    try:
        numbers = list(map(int, user_input.split()))
        
        # Check if exactly 4 numbers are provided
        if len(numbers) != 4:
            await update.message.reply_text("Please provide exactly four numbers.")
            return

        # Generate combinations and totals
        combinations_dict = generate_combinations(numbers)
        
        # Send the results
        if combinations_dict:
            response = "\n".join([f"Total: {total} -> Combination: {comb}" for total, comb in sorted(combinations_dict.items())])
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("No valid totals found between 10 and 100 for the given numbers.")
    
    except ValueError:
        await update.message.reply_text("Please send valid numbers separated by spaces.")

# Main function to run the bot
def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token("7634135469:AAEDxCSCHUBaPrhoASgEzLn4TqEuydcc3a4").build()

    # Add command handler to start the bot
    application.add_handler(CommandHandler("start", start))

    # Add message handler to process numbers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_numbers))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()

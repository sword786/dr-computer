import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters
from itertools import permutations, product
import logging

# Enable nested event loop for Jupyter notebooks
nest_asyncio.apply()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to calculate possible totals between 10 and 100
def calculate_totals(numbers):
    operations = ['+', '-', '*', '/']
    results = set()
    explanations = {}

    # Generate all possible combinations of numbers and operations
    for num_count in range(2, 5):  # Considering 2, 3, and 4 numbers
        for nums in permutations(numbers, num_count):
            for ops in product(operations, repeat=num_count - 1):
                # Build expressions respecting precedence with parentheses
                expr = str(nums[0])
                for i in range(len(ops)):
                    expr = f"({expr} {ops[i]} {nums[i + 1]})"
                try:
                    # Evaluate the expression and filter results between 10 and 100
                    result = eval(expr)
                    if result is not None and 10 <= result <= 100 and result == int(result):
                        result_int = int(result)
                        results.add(result_int)
                        explanations[result_int] = expr  # Save the expression for each result
                except:
                    continue

    return sorted(results), explanations

# Function to handle the /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Please enter 4 numbers between 1 and 9 (without spaces, e.g., 1234)."
    )

# Function to handle number input
async def handle_numbers(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()

    # Ensure the user input is valid
    if len(user_input) == 4 and user_input.isdigit() and all('1' <= char <= '9' for char in user_input):
        numbers = [int(char) for char in user_input]
        results, explanations = calculate_totals(numbers)

        # Store explanations in context for future requests
        context.user_data["explanations"] = explanations
        context.user_data["numbers"] = numbers

        # Display results with buttons
        if results:
            keyboard = [
                [InlineKeyboardButton(str(result), callback_data=f"result_{result}") for result in results[i:i+8]]
                for i in range(0, len(results), 8)
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"The possible totals between 10 and 100 for {numbers} are:\n\n{', '.join(map(str, results))}\n\nClick a result for an explanation.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(f"No valid results found for {numbers}.")
    else:
        await update.message.reply_text("Invalid input. Please enter 4 numbers between 1 and 9 (e.g., 1234).")

# List of combinations for /prostart
COMBINATIONS = [
    "1223", "1224", "1225", "1226", "1227", "1228", "1229", "1233", "1234", "1235",
    "1236", "1237", "1238", "1239", "1244", "1245", "1246", "1247", "1248", "1249",
    "1255", "1256", "1257", "1258", "1259", "1266", "1267", "1268", "1269", "1277",
    "1278", "1279", "1288", "1289", "1299", "1334", "1335", "1336", "1337", "1338",
    "1339", "1344", "1345", "1346", "1347", "1348", "1349", "1355", "1356", "1357",
    "1358", "1359", "1366", "1367", "1368", "1369", "1377", "1378", "1379", "1388",
    "1389", "1399", "1445", "1446", "1447", "1448", "1449", "1455", "1456", "1457",
    "1458", "1459", "1466", "1467", "1468", "1469", "1477", "1478", "1479", "1488",
    "1489", "1499", "1556", "1557", "1558", "1559", "1566", "1567", "1568", "1569",
    "1577", "1578", "1579", "1588", "1589", "1599", "1667", "1668", "1669", "1677",
    "1678", "1679", "1688", "1689", "1699", "1778", "1779", "1788", "1789", "1799",
    "1889", "1899"
]

# Function to handle /prostart command
async def prostart(update: Update, context: CallbackContext):
    first_half = COMBINATIONS[:56]
    second_half = COMBINATIONS[56:]

    # Create first set of buttons
    first_half_buttons = [
        [InlineKeyboardButton(combo, callback_data=f"combo_{combo}") for combo in first_half[i:i+6]]
        for i in range(0, len(first_half), 6)
    ]
    first_half_markup = InlineKeyboardMarkup(first_half_buttons)

    # Create second set of buttons
    second_half_buttons = [
        [InlineKeyboardButton(combo, callback_data=f"combo_{combo}") for combo in second_half[i:i+6]]
        for i in range(0, len(second_half), 6)
    ]
    second_half_markup = InlineKeyboardMarkup(second_half_buttons)

    # Send the first message
    await update.message.reply_text(
        "Select a combination of numbers (Part 1):",
        reply_markup=first_half_markup
    )

    # Send the second message
    await update.message.reply_text(
        "Select a combination of numbers (Part 2):",
        reply_markup=second_half_markup
    )

# Function to handle combination selection
async def handle_combination(update: Update, context: CallbackContext):
    query = update.callback_query
    combination = query.data.split("_")[1]

    numbers = [int(char) for char in combination]
    results, explanations = calculate_totals(numbers)

    context.user_data["explanations"] = explanations
    context.user_data["numbers"] = numbers

    if results:
        keyboard = [
            [InlineKeyboardButton(str(result), callback_data=f"result_{result}") for result in results[i:i+8]]
            for i in range(0, len(results), 8)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"The possible totals for the combination {combination} are:\n\n{', '.join(map(str, results))}\n\nClick a result for an explanation.",
            reply_markup=reply_markup
        )
    else:
        await query.message.reply_text(f"No valid results found for the combination {combination}.")
    await query.answer()

# Function to handle explanation request
async def explain(update: Update, context: CallbackContext):
    query = update.callback_query
    result = int(query.data.split("_")[1])

    explanations = context.user_data.get("explanations", {})
    explanation = explanations.get(result, None)

    if explanation:
        response = f"The result {result} is obtained by the following operation:\n{explanation}"
    else:
        response = f"Sorry, I couldn't find an explanation for {result}."

    await query.answer()
    await query.message.reply_text(response)

# Function to handle the /total command
async def total(update: Update, context: CallbackContext):
    totals_buttons = [
        [InlineKeyboardButton(str(i), callback_data=f"total_{i}") for i in range(start, min(start + 8, 101))]
        for start in range(10, 101, 8)
    ]
    reply_markup = InlineKeyboardMarkup(totals_buttons)
    await update.message.reply_text("Select a total between 10 and 100:", reply_markup=reply_markup)

# Function to handle total selection
async def handle_total_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    selected_total = int(query.data.split("_")[1])

    # Generate explanations for all predefined combinations
    explanations = {}
    for combination in COMBINATIONS:
        numbers = [int(char) for char in combination]
        _, combo_explanations = calculate_totals(numbers)
        for total, expr in combo_explanations.items():
            if total not in explanations:
                explanations[total] = []
            explanations[total].append((combination, expr))

    context.user_data["explanations"] = explanations

    # Fetch combinations for the selected total
    possible_combinations = explanations.get(selected_total, [])

    if possible_combinations:  # Ensure there are combinations to display
        # Display combinations as inline buttons in rows of 6
        combination_buttons = [
            [InlineKeyboardButton(combo, callback_data=f"explain_{combo}") for combo, _ in possible_combinations[i:i+6]]
            for i in range(0, len(possible_combinations), 6)
        ]
        reply_markup = InlineKeyboardMarkup(combination_buttons)

        await query.message.reply_text(
            f"Possible combinations for total {selected_total}:",
            reply_markup=reply_markup
        )
    else:
        await query.message.reply_text(f"No combinations found for total {selected_total}.")
    await query.answer()

# Function to handle combination explanation
async def explain_combination(update: Update, context: CallbackContext):
    query = update.callback_query
    combination = query.data.split("_")[1]

    # Retrieve explanations from user data
    explanations = context.user_data.get("explanations", {})

    # Find the total and explanation for the selected combination
    explanation = None
    for total, combos in explanations.items():
        for combo, expr in combos:
            if combo == combination:
                explanation = expr
                break
        if explanation:
            break

    if explanation:
        response = f"The result for {combination} is derived from the operation:\n{explanation}"
    else:
        response = f"Sorry, no explanation found for {combination}."

    await query.message.reply_text(response)
    await query.answer()

def main():
    # Set up the application and handlers
    application = Application.builder().token('7854389497:AAGUtnpgOJ2CJTT4uOxOTtQnp7cguBxjroA').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))
    application.add_handler(CommandHandler('total', total))
    application.add_handler(CallbackQueryHandler(handle_total_selection, pattern='^total_'))
    application.add_handler(CallbackQueryHandler(handle_combination, pattern='^combo_'))
    application.add_handler(CallbackQueryHandler(explain, pattern='^result_'))
    application.add_handler(CommandHandler('prostart', prostart))
    application.add_handler(CallbackQueryHandler(explain_combination, pattern='^explain_'))


    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()

from robocorp.tasks import task
from robocorp import browser
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Tables import Table
from RPA.PDF import PDF


ORDERS_CSV_URL = "https://robotsparebinindustries.com/orders.csv"
ROBOT_ORDER_PAGE = "https://robotsparebinindustries.com/#/robot-order"
ORDERS_LOCAL_PATH = "orders.csv"
ORDERS_HEADER = ["Order number","Head","Body","Legs","Address"]

def open_robot_order_website() -> None:
    """
    Opens the robot order website
    """
    browser.goto(ROBOT_ORDER_PAGE)

def configure_browser() -> None:
    """
    Slows down the Robot
    """
    browser.configure(
        slowmo=500,
    )

def download_and_read_orders() -> Table:
    """
    Downloads and reads the orders into a table

    Returns:
        Table: the table form of the csv data file
    """
    # download file
    http = HTTP()
    http.download(url=ORDERS_CSV_URL, overwrite=True)
    # convert csv to table format
    csv = Tables()
    return csv.read_table_from_csv(ORDERS_LOCAL_PATH, columns=ORDERS_HEADER)

def give_up_rights() -> None:
    """
    Click the rights popup
    """
    page = browser.page()
    page.click("text=OK")

def fill_form_and_submit(table_data: Table) -> None:
    """
    Fills out the order form for every entry in the table

    Args:
        table_data (Table): order data 
    """
    page = browser.page()
    for row in table_data:
        # head form
        page.select_option("#head", str(row['Head']))
        # body
        page.click(f'#id-body-{str(row["Body"])}')
        # legs
        page.fill('css=input[type="number"]', str(row["Legs"]))
        # address
        page.fill("#address", str(row["Address"]))
        # preview and order
        page.click("#preview")
        screenshot_robot(str(row["Order number"]))
        page.click("#order")
        while page.query_selector('css=div[class="alert alert-danger"]') is not None:
            page.click("#order")
        # order another
        store_receipt_as_pdf(str(row["Order number"]))
        page.click("#order-another")
        give_up_rights()

def screenshot_robot(order_number: str) -> None:
    """
    Take picture of robot preview

    Args:
        order_number (str): order number of the robot 
    """
    page = browser.page()
    page.screenshot(path=f"output/previews/robot_preview_{order_number}.png")
    

def store_receipt_as_pdf(order_number: str) -> None:
    """
    Create final receipt and store as pdf

    Args:
        order_number (str): order number of the robot 
    """
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, f"output/receipt/order_receipt_{order_number}.pdf")
    pdf.add_files_to_pdf(files=[f"output/receipt/order_receipt_{order_number}.pdf", f"output/previews/robot_preview_{order_number}.png"], 
                         target_document=f"output/receipt/order_receipt_{order_number}.pdf")
    

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    configure_browser()
    open_robot_order_website()
    table_data = download_and_read_orders()
    give_up_rights()
    fill_form_and_submit(table_data)
    


import logging
import os
import pymongo
import azure.functions as func
from bson.objectid import ObjectId
from bson.json_util import dumps
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the connection string from environment variables
CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Set up the MongoDB client
client = pymongo.MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger", methods=["GET"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function HTTP GET trigger received a request.')

    try:
        # Extract the '_id' parameter from the query string
        document_id = req.params.get('_id')
        if not document_id:
            return func.HttpResponse("Missing '_id' parameter in the query string.", status_code=400)

        try:
            object_id = ObjectId(document_id)
        except:
            return func.HttpResponse("Invalid '_id' format. Must be a valid ObjectId.", status_code=400)

        # Query the MongoDB collection for the document with the specified '_id'
        document = collection.find_one({'_id': object_id})

        if document:
            # Convert the document to a JSON string and return it
            return func.HttpResponse(dumps(document), status_code=200, mimetype="application/json")
        else:
            return func.HttpResponse(f"Document with id {document_id} not found.", status_code=404)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

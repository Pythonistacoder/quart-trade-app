from quart import Quart, Blueprint
from quart_cors import cors

from routes.login import login
from service.background_task import background_task
from utils.square_off import sqaure_off



app = Quart(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app = cors(app, allow_origin="*")
@app.get("/start")
async def start_process():
    try:
        app.add_background_task(background_task)
        return {"message":"Background process started"}
    except:
        return {"message":"Kindly login first"}
@app.route("/stop")
async def stop_background_tasks():
    """
        On being deployed if we need to manually stop the background task then
        this route is used
    """
    for task in app.background_tasks:
        task.cancel()
    sqaure_off()
    return {"message":"All task cancelled"}
resource_list:Blueprint=[login]
for resource in resource_list:
    app.register_blueprint(blueprint=resource)



if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=80)
    app.run(port=8080)
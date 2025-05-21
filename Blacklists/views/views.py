import uuid
import re
import os

from config import Config

from flask import request, abort, make_response, Response
from flask_restful import Resource
from models import db, Blacklist, BlacklistSchema

blacklist_schema = BlacklistSchema()
blacklists_schema = BlacklistSchema(many=True)

class HeaderResource(Resource):
    """
    Clase base con el método de autorización .
    """
    def authorize_request(self):
        """
        Valida el header de la autorización y retorna 200 d si el token es válido.
        """
        print(f"License key: {os.getenv('NEW_RELIC_LICENSE_KEY')}")
        authorization_header = request.headers.get('Authorization')
        
        try:
            if not authorization_header:
                abort(Response(status=403))

            token = authorization_header.split(" ")[1] if authorization_header.startswith("Bearer ") else None            
            if not token:
                abort(Response(status=403))
                
            if token == Config.AUTH_TOKEN:
                return True
            else:
                abort(Response(status=403))
            
        except (IndexError, ValueError):
            abort(make_response('', 401))


class BlacklistView(HeaderResource):

    def post(self):
        print(f"License key: {os.getenv('NEW_RELIC_LICENSE_KEY')}")
        self.authorize_request()
        data = request.get_json()

        required_fields = ["email", "app_uuid", "blocked_reason"]
        for field in required_fields:
            if field not in data:
                response = make_response('', 400)
                abort(response)
        
        email = data["email"]
        if not self.validate_email(email):
            abort(Response(status=400))
            
        if self.account_exists(email):
            abort(Response(status=412))       

        try:

            new_blacklist = Blacklist(
                id=str(uuid.uuid4()),
                email=data["email"],
                app_uuid=data["app_uuid"],
                blocked_reason=data["blocked_reason"],
                ip= request.remote_addr                                
            )

            db.session.add(new_blacklist)
            db.session.commit()

            return {
                       "id": new_blacklist.id,
                       "msg": "Cuenta creada correctamente"                       
                   }, 201

        except Exception as e:
            return {'message': f'Hubo un problema al crear la cuenta: {str(e)}'}, 500
    
    def validate_email(self, email):
        """
        Valida el formato del email utilizando una expresión regular.
        """
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None

    def account_exists(self, email):
        """
        Verifica si ya existe una cuenta con el mismo email.
        """
        return db.session.query(Blacklist).filter((Blacklist.email == email)).first() is not None

class BlacklistDetailView(HeaderResource):

    def get(self, email):
        """
        Retorna una cuenta del balcklist, solo un usuario autorizado puede realizar esta operación.
        """
        print(f"License key: {os.getenv('NEW_RELIC_LICENSE_KEY')}")
        self.authorize_request()
        try:
            if not email:
                make_response('', 400)
        except ValueError:
            response = make_response('', 400)
            abort(response)
            
        if not BlacklistView.validate_email(self, email):
            abort(Response(status=400))

        try:
            cuenta = Blacklist.query.filter_by(email=email).first()
        except Exception as e:            
            return {'msg': f'Hubo un problema al consultar la cuenta: {str(e)}'}, 500
        
        if not cuenta:
            return {
                       "existe": False,
                       "blocked_reason": ""                       
                   }, 200
        else:
            return {
                       "existe": True,
                       "blocked_reason": cuenta.blocked_reason                       
                   }, 200
            
class HealthCheckView(Resource):
    def get(self):
        """
        Usado para verificar el estado del servicio.
        """
        return "pong", 200

class ResetDatabaseView(Resource):
    def post(self):
        """
        Usado para limpiar la base de datos del servicio.
        """
        try:
            db.session.query(Blacklist).delete()
            db.session.commit()
            return {"msg": "Todos los datos fueron eliminados"}, 200

        except Exception as e:
            db.session.rollback()
            return {'msg': f'Hubo un problema al eliminar la base de datos: {str(e)}'}, 500       

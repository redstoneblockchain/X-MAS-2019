import jwt, base64, json

JWTSecret = "d12ic01n9diS0CDNWIC0diadscj12n9c1dsaocpsapda"
SantaSecret = "aojaics9samiocdassacpodasidnpc1c1cw_sa-mi_bag_picioarele_ce_lung_e_secretu_asta"

def DecodeB64 (inp):
	return base64.b64decode (inp + "==").decode ("utf-8").replace ("\x00", "")

def DecodeJWT (token):
	userData = {}
	
	try:
		userData = jwt.decode (token, JWTSecret, algorithm = 'HS256')
	except:
		try:
			token = token.split (".")

			if (token[2] == ""):
				alg = json.loads (DecodeB64 (token[0]))

				if (alg["alg"].lower () == "none"):
					userData = json.loads (DecodeB64 (token[1]))
		except:
			pass

	return userData

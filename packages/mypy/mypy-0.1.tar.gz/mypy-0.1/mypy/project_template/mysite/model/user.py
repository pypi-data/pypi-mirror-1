class UserGroup(McModel):    #id user_id group
    pass

class UserDetail(McModel):   #id career
    pass

class UserLog(McModel):      #id register_time last_login_time
    pass

class UserEmail(McModel):    #id email
    pass

class UserPasswd(McModel): #id passwd_hash
    pass

class UserSession(McModel): #id session create_time
    pass

class UserWaitingConfirm(Model): #id email ck
    pass

class User(McModel):   #id name url picver
    def register(self,email):
        pass

    def confirm_email(self,id,ck):
        return True

    def login(self,email,passwd):
        return session

    def logout(self,id):
        pass
    
    @classmethod
    def by_email(self,email):
        pass

    @classmethod
    def by_id(self,id):
        pass

    @classmethod
    def by_session(self,id,session):
        return True
import os

class uploadfile():
    def __init__(self, name, type=None, size=None, not_allowed_msg='', job_id = None):
        self.name = name
        self.type = type
        self.size = size
        self.not_allowed_msg = not_allowed_msg
        self.url = os.path.join("/api/1/jobs/", "%d" % (job_id, ), 'upload', name)
        self.thumbnail_url = self.delete_url = os.path.join("/api/1/jobs/", "%d" % (job_id, ), 'thumbnail', name)
        self.delete_url = os.path.join("/api/1/jobs/", "%d" % (job_id, ), 'delete', name)
        self.delete_type = "DELETE"


    def get_file(self):
        if self.type != None:
            # POST an normal file
            if self.not_allowed_msg == '':
                return {"name": self.name,
                        "type": self.type,
                        "size": self.size, 
                        "url": self.url, 
                        "deleteUrl": self.delete_url, 
                        "deleteType": self.delete_type,}

            # File type is not allowed
            else:
                return {"error": self.not_allowed_msg,
                        "name": self.name,
                        "type": self.type,
                        "size": self.size,}

        # GET normal file from disk
        else:
            return {"name": self.name,
                    "size": self.size, 
                    "url": self.url, 
                    "deleteUrl": self.delete_url, 
                    "deleteType": self.delete_type,}

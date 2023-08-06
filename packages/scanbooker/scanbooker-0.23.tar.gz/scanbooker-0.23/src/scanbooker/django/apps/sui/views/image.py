from dm.view.base import *

class SafetyTrainingCertificateView(AbstractImageView):

    domainClassName = 'SafetyTrainingCertificate'

    def getImageContent(self):
        domainObject = self.getDomainObject()
        return domainObject.file

    def getImageContentType(self):
        domainObject = self.getDomainObject()
        return domainObject.contentType


def read(request, certificateId=''):
    view = SafetyTrainingCertificateView(
        request=request, domainObjectKey=int(certificateId)
    )
    return view.getResponse()


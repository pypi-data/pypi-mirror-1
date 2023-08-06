
def getAttachments(context):
    attachments = []
    contents = context.getFolderContents(contentFilter={'portal_type': ['FileAttachment']})
    upPos = 0
    for attachment in contents:
        values = {'id' : attachment.getId,
                  'title' : attachment.Title,
                  'url' : attachment.getURL,
                  'size' : attachment.getObjSize,
                  'upPos' : upPos,
                  'downPos' : context.getObjectPosition(attachment.getId),
                  }
        upPos = values['downPos']
        if len(attachments) > 0:
            attachments[-1]['downPos'] = upPos
        attachments.append(values)
    return attachments

def getImages(context):
    images = []
    contents = context.getFolderContents(contentFilter={'portal_type': ['ImageAttachment']}, full_objects=True)
    upPos = 0
    for image in contents:
        values = {'id' : image.getId(),
                  'title' : image.Title(),
                  'url' : image.absolute_url(),
                  'tag' : image.tag(scale='tile'),
                  'height' : image.height,
                  'width' : image.width,
                  'size' : image.getObjSize(),
                  'upPos' : upPos,
                  'downPos' : context.getObjectPosition(image.getId()),
                  }
        upPos = values['downPos']
        if len(images) > 0:
            images[-1]['downPos'] = upPos
        images.append(values)
    return images

def getLinks(context):
    links = []
    contents = context.getFolderContents(contentFilter={'portal_type': ['LinkAttachment']})
    upPos = 0
    for link in contents:
        values = {'id' : link.getId,
                  'title' : link.Title,
                  'url' : link.getRemoteUrl,
                  'upPos' : upPos,
                  'downPos' : context.getObjectPosition(link.getId),
                  }
        upPos = values['downPos']
        if len(links) > 0:
            links[-1]['downPos'] = upPos
        links.append(values)
    return links
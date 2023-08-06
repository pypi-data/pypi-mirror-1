from qi.jwMedia.content.video import FlashVideo

def getFilePath(self):
	return self.context.title()
FlashVideo.getFilePath = getFilePath
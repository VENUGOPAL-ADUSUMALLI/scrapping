from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from webscrapper.db_hits import get_data  # make sure the import is correct

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        from_number = request.POST.get('From')
        body = request.POST.get('Body')

        # print(f"📩 Message from {from_number}: {body}")


        reply_text = get_data()


        response = MessagingResponse()
        response.message(reply_text)

        return HttpResponse(str(response), content_type='text/xml')

    return HttpResponse("Only POST allowed", status=405)

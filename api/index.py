def handler(request, context):
    """Vercel serverless function"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': {
            'message': 'Decision Assistant API is running!',
            'path': request.url,
            'method': request.method
        }
    }

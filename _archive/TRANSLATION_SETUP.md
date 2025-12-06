# Google Cloud Translation API Setup Guide

## Problem Description

The translation feature currently returns an error message:
```
Google Cloud Translation API is not enabled. Please enable it in your GCP project console.
```

This is because the Google Cloud Translation API has not been enabled in your GCP project.

## Solution

### Method 1: Enable via GCP Console (Recommended)

1. **Access Google Cloud Console**
   - Open your browser and visit: https://console.cloud.google.com/

2. **Select Your Project**
   - Ensure you have selected the project: `apcomp215-group88` (Project ID: 748223712605)

3. **Enable Translation API**
   - Visit: https://console.cloud.google.com/apis/library/translate.googleapis.com
   - Or alternatively:
     - Select "APIs & Services" > "Library" from the left menu
     - Search for "Cloud Translation API"
     - Click on "Cloud Translation API"
     - Click the "Enable" button

4. **Wait for Activation**
   - API enablement typically takes a few minutes to take effect

5. **Test Translation Functionality**
   - Refresh your frontend page
   - Test Chinese text translation again
   - You should see correct English translation results

### Method 2: Enable via Command Line

If you have `gcloud` CLI installed:

```bash
# Set the project
gcloud config set project apcomp215-group88

# Enable Translation API
gcloud services enable translate.googleapis.com

# Verify API is enabled
gcloud services list --enabled | grep translate
```

## Verify Configuration

After enabling the API, you can verify using the following methods:

### 1. Test Backend via curl

```bash
curl -X POST http://localhost:9000/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"患者跌倒受伤"}' | python3 -m json.tool
```

Successful response should look like:
```json
{
    "original_text": "患者跌倒受伤",
    "detected_lang": "zh",
    "translated_text": "Patient fell and was injured",
    "was_translated": true,
    "engine": "google_translate",
    "error": null
}
```

### 2. Test via Frontend

1. Enter Chinese text on the frontend classification page
2. System should automatically detect language and translate
3. View the translation result displaying correct English

## Pricing Information

- Google Cloud Translation API is billed by usage
- First 500,000 characters/month are free
- Beyond that: $20/million characters
- For testing and development use, typically within free tier

Detailed pricing: https://cloud.google.com/translate/pricing

## Frequently Asked Questions

### Q: API still not working after enabling?

A: 
1. Wait 5-10 minutes for changes to propagate
2. Restart backend container: `docker restart safety-event-api`
3. Check service account has correct permissions

### Q: How to verify successful enablement?

A: Run the following command to check:
```bash
gcloud services list --enabled --project=apcomp215-group88 | grep translate
```

You should see:
```
translate.googleapis.com    Cloud Translation API
```

### Q: What permissions does the service account need?

A: Ensure the service account has one of the following roles:
- `roles/cloudtranslate.user` - Use Translation API
- `roles/editor` - Editor (includes translation permissions)
- `roles/owner` - Owner (includes all permissions)

## Temporary Workaround

If you cannot enable the API temporarily, the system will:
1. Detect non-English text
2. Return original text marked as untranslated
3. Still allow classification using original text (may have reduced accuracy)

## Related Documentation

- Cloud Translation API Documentation: https://cloud.google.com/translate/docs
- API Enablement Guide: https://cloud.google.com/apis/docs/getting-started
- Service Account Configuration: https://cloud.google.com/iam/docs/service-accounts

## Contact Support

If you encounter issues:
1. Check GCP project configuration
2. Verify service account permissions
3. View backend container logs: `docker logs safety-event-api`
4. Contact project administrator or GCP support

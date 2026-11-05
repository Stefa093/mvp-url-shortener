# Mini URL Shortener API

A lightweight URL shortening service built with **Python and FastAPI** as part of a technical hiring challenge.

The goal of this project is to deliver a functional Minimum Viable Product (MVP) within the specified **3-hour time limit**, prioritizing simplicity, code readability, core functionality, and automated testing.

## 1\. Features

The MVP implements the following functionality:

-   **URL Shortening:** Generate a unique six-character alphanumeric code for a valid HTTP or HTTPS URL.
-   **URL Redirection:** Redirect short URLs to their original destinations using HTTP 302.
-   **Click Analytics:** Record individual click events, including timestamps and User-Agent information.
-   **Statistics:** Retrieve the original URL, total clicks, creation date, and last click timestamp.
-   **URL Validation:** Return HTTP 400 for invalid HTTP/HTTPS URLs.
-   **Error Handling:** Return HTTP 404 for unknown short codes.
-   **HEAD Support:** Inspect redirect headers without incrementing the click counter.
-   **Automated Tests:** Verify the main API functionality using pytest.

## 2\. Tech Stack

-   Python 3.11+
-   FastAPI
-   Pydantic
-   Uvicorn
-   pytest
-   HTTPX

**Storage:** In-memory Python dictionary.

## 3\. Project Structure

mini-url-shortener/  
├── app/  
│   ├── \_\_init\_\_.py  
│   └── main.py  
├── tests/  
│   └── test\_main.py  
├── requirements.txt  
├── README.md  
└── .gitignore

## 4\. Installation

Clone the repository:

git clone [https://github.com/Stefa093/mvp-url-shortener.git](https://github.com/Stefa093/mvp-url-shortener.git)  
cd mvp-url-shortener

Create a virtual environment on macOS or Linux:

python3 -m venv .venv  
source .venv/bin/activate

Install the required dependencies:

```
python -m pip install -r requirements.txt
```

## 5\. Running the Application

Start the development server:

```
uvicorn app.main:app --reload
```

The API will be available at:

[http://127.0.0.1:8000](http://127.0.0.1:8000/)

FastAPI automatically generates interactive API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 6\. API Endpoints

### POST /shorten — Create a Short URL

curl -X POST [http://127.0.0.1:8000/shorten](http://127.0.0.1:8000/shorten) \\  
  -H "Content-Type: application/json" \\  
  -d '{"url":"[https://example.com](https://example.com/)","label":"Example"}'

Example response:

{  
  "code": "aB7xQ2",  
  "short\_url": "[http://127.0.0.1:8000/aB7xQ2](http://127.0.0.1:8000/aB7xQ2)"  
}

Returns HTTP 201 when successful.

### GET /{code} — Redirect

```
curl -i http://127.0.0.1:8000/aB7xQ2
```

Returns HTTP 302 with the original destination in the `Location` header.

Each successful GET redirection records a click event.

### HEAD /{code} — Inspect Redirect

```
curl -I http://127.0.0.1:8000/aB7xQ2
```

Returns redirect headers without increasing the click counter.

### GET /stats/{code} — Retrieve Statistics

```
curl http://127.0.0.1:8000/stats/aB7xQ2
```

Example response:

{  
  "code": "aB7xQ2",  
  "original\_url": "[https://example.com/](https://example.com/)",  
  "label": "Example",  
  "created\_at": "2026-11-05T12:00:00+00:00",  
  "total\_clicks": 3,  
  "last\_clicked\_at": "2026-11-05T12:15:00+00:00"  
}

All codes and timestamps shown above are illustrative.

### Error Handling

| Scenario                        | HTTP Status |
| ------------------------------- | ----------- |
| Successful URL creation         | 201         |
| Successful redirection          | 302         |
| Invalid HTTP/HTTPS URL          | 400         |
| Unknown short code              | 404         |
| Missing required request fields | 422         |

## 7\. Automated Testing

Run the automated tests:

```
python -m pytest -v
```

Tests cover:

-   Creating a shortened URL.
-   Redirecting to the original URL.
-   Recording click events.
-   Rejecting invalid URLs.
-   Handling unknown short codes.

## 8\. Design Notes

1.  I selected an in-memory dictionary to keep the MVP simple and respect the three-hour time constraint.
2.  Short codes contain six alphanumeric characters generated using Python's `secrets` module.
3.  Existing codes are checked to reduce collision risks within the running process.
4.  Pydantic validates HTTP/HTTPS URLs, with explicit HTTP 400 error handling.
5.  Clicks are recorded as individual events to support basic analytics and future extensions.
6.  HEAD requests are handled separately to allow redirect inspection without recording clicks.
7.  Functions are kept small and readable to simplify maintenance and testing.
8.  The in-memory approach does not provide persistence or concurrency-safe uniqueness across multiple processes.
9.  A production version would require persistent storage, stronger security controls, and improved scalability.

## 9\. Future Improvements

The following features are **proposed enhancements and are not included in the current MVP**.

I would prioritize them based on business value, implementation complexity, and the time available.

### Priority 1 — Custom Short Codes

Allow users to specify their own memorable short codes instead of always receiving randomly generated ones.

For example:

{  
  "url": "[https://example.com](https://example.com/)",  
  "label": "Marketing Campaign",  
  "custom\_code": "black-friday"  
}

Result:

[`http://localhost:8000/black-friday`](http://localhost:8000/black-friday)

**Benefits:**

-   More memorable and user-friendly links.
-   Useful for marketing campaigns and branded URLs.
-   Better user control.

Implementation would include code-format validation, reserved-route protection, and HTTP 409 conflict handling when a code is already in use.

### Priority 2 — Daily Click Analytics

Extend the statistics endpoint to provide click counts grouped by date.

Example:

{  
  "code": "aB7xQ2",  
  "total\_clicks": 15,  
  "daily\_clicks": {  
    "2026-11-03": 4,  
    "2026-11-04": 6,  
    "2026-11-05": 5  
  }  
}

**Benefits:**

-   Identify usage trends.
-   Analyze link activity over time.
-   Provide useful information for marketing and reporting.

This could be implemented by aggregating the timestamps already recorded in click events.

### Priority 3 — Health Check Endpoint

Introduce:

`GET /health`

Example response:

{  
  "status": "ok"  
}

This provides a simple way for monitoring systems to verify that the application is responding.

### Priority 4 — Security and Abuse Prevention

Introduce additional security measures to reduce misuse of the URL shortening service.

Potential improvements include:

-   Domain blocklists and URL safety checks.
-   Rate limiting per IP address.
-   Restrictions against redirection to internal or unauthorized destinations.
-   Basic abuse monitoring.

These measures would require further design and testing before production deployment.

### Priority 5 — Persistent Storage

Replace the in-memory dictionary with SQLite or PostgreSQL.

**Benefits:**

-   Preserve links and analytics after server restarts.
-   Support a growing number of stored URLs.
-   Enable database-level uniqueness constraints.
-   Improve support for concurrent requests.

### Additional Features Suggested in the Challenge

If more time were available, I would also consider implementing the optional requirements from the assignment:

-   Bulk URL creation through `POST /shorten/bulk`.
-   Optional link expiration with HTTP 410 responses.
-   QR code generation through `GET /qr/{code}`.
-   Support for preserving or appending UTM parameters.

## 10\. Limitations

This project is intentionally designed as a time-boxed MVP rather than a production-ready service.

Current limitations include:

-   Data is lost when the application process restarts.
-   Storage is not shared between multiple server processes.
-   No authentication or user management.
-   Limited protection against malicious URLs and automated abuse.
-   Basic analytics without advanced filtering or reporting.
-   No persistent database or concurrency-safe code reservation.

These limitations were accepted to prioritize the core requirements within the available development time.

## 11\. Conclusion

This project demonstrates a practical approach to building a small REST API with Python and FastAPI.

The focus was on delivering the required functionality, implementing basic validation and automated tests, and keeping the architecture simple enough to understand and extend.

With additional development time, the next priorities would be **custom short codes, daily click analytics, and persistent storage**, followed by stronger security and operational monitoring.
# API Design: Disaster Management System

This document outlines the high-level API design for the backend services.

## Authentication

### `POST /auth/otp`

*   **Description:** Sends an OTP to the user's phone number.
*   **Request Body:**
    *   `phone_number` (string, required): The user's phone number.
*   **Response:**
    *   `message` (string): "OTP sent successfully."

### `POST /auth/verify`

*   **Description:** Verifies the OTP and returns a JWT token.
*   **Request Body:**
    *   `phone_number` (string, required): The user's phone number.
    *   `otp` (string, required): The OTP received by the user.
*   **Response:**
    *   `token` (string): JWT token for authenticated sessions.

## Incidents

### `POST /incidents`

*   **Description:** Allows users to report a new incident.
*   **Authentication:** Required.
*   **Request Body:**
    *   `latitude` (float, required): Latitude of the incident.
    *   `longitude` (float, required): Longitude of the incident.
    *   `description` (string): Description of the incident.
    *   `photo` (file): Photo of the incident.
*   **Response:**
    *   `id` (integer): The ID of the newly created incident.
    *   `message` (string): "Incident reported successfully."

### `GET /incidents`

*   **Description:** Retrieves a list of incidents.
*   **Authentication:** Required.
*   **Query Parameters:**
    *   `latitude` (float): User's current latitude.
    *   `longitude` (float): User's current longitude.
    *   `radius` (integer): Radius in kilometers to search for incidents.
*   **Response:**
    *   A list of incident objects.

## Disaster Events

### `GET /events`

*   **Description:** Retrieves a list of recent disaster events.
*   **Authentication:** Required.
*   **Query Parameters:**
    *   `type` (string): Filter by disaster type ('earthquake', 'flood', 'wildfire').
    *   `latitude` (float): User's current latitude.
    *   `longitude` (float): User's current longitude.
    *   `radius` (integer): Radius in kilometers to search for events.
*   **Response:**
    *   A list of disaster event objects.

## Alerts

### `GET /alerts`

*   **Description:** Retrieves alerts for the authenticated user.
*   **Authentication:** Required.
*   **Response:**
    *   A list of alert objects.

## Safe Zones

### `GET /safe-zones`

*   **Description:** Retrieves a list of safe zones.
*   **Authentication:** Required.
*   **Query Parameters:**
    *   `latitude` (float): User's current latitude.
    *   `longitude` (float): User's current longitude.
    *   `radius` (integer): Radius in kilometers to search for safe zones.
*   **Response:**
    *   A list of safe zone objects.

## Resources

### `GET /resources`

*   **Description:** Retrieves a list of resources (shelters, hospitals, etc.).
*   **Authentication:** Required.
*   **Query Parameters:**
    *   `type` (string): Filter by resource type.
    *   `latitude` (float): User's current latitude.
    *   `longitude` (float): User's current longitude.
    *   `radius` (integer): Radius in kilometers to search for resources.
*   **Response:**
    *   A list of resource objects.

## Crowdsourced Reports

### `POST /crowdsourced-reports`

*   **Description:** Allows users to submit a crowdsourced report.
*   **Authentication:** Required.
*   **Request Body:**
    *   `report_type` (string, required): Type of report ('road_blocked', 'bridge_down').
    *   `latitude` (float, required): Latitude of the report.
    *   `longitude` (float, required): Longitude of the report.
    *   `description` (string): Description of the report.
*   **Response:**
    *   `id` (integer): The ID of the newly created report.
    *   `message` (string): "Report submitted successfully."

import requests

class DrugInfoService:
    """
    Wrapper around the OpenFDA Drug Label API.

    This service provides methods to retrieve public drug information
    such as name, manufacturer, purpose, and warnings from the
    official OpenFDA API.

    See:
        https://open.fda.gov/apis/drug/label/
    """

    BASE_URL = "https://api.fda.gov/drug/label.json"

    @classmethod
    def get_drug_info(cls, drug_name: str):
        """
        Retrieve drug label information for a given medication name.

        This method queries the OpenFDA "drug/label" endpoint for
        a specific generic drug name and returns a simplified
        dictionary of relevant information.

        Args:
            drug_name (str): The name of the medication to search for.
                Must be a non-empty string corresponding to the
                generic name field in the OpenFDA database.

        Returns:
            dict: A dictionary containing the following keys:
                - `name` (str): The generic drug name (or input name).
                - `manufacturer` (str): The manufacturer's name.
                - `warnings` (list[str]): Any warnings from the drug label.
                - `purpose` (list[str]): Stated purposes or indications.

        Raises:
            ValueError:
                - If `drug_name` is missing or empty.
                - If the OpenFDA API returns a non-200 response.
                - If no results are found for the given drug name.

            requests.exceptions.RequestException:
                - If there is a network error or timeout during the request.

        Example:
            >>> DrugInfoService.get_drug_info("ibuprofen")
            {
                "name": "Ibuprofen",
                "manufacturer": "McKesson",
                "warnings": ["Keep out of reach of children."],
                "purpose": ["Pain reliever/fever reducer"]
            }
        """
        
        if not drug_name:
            raise ValueError("drug_name is required")

        params = {"search": f"openfda.generic_name:{drug_name.lower()}", "limit": 1}

        resp = requests.get(cls.BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            raise ValueError(f"OpenFDA API error: {resp.status_code}")

        data = resp.json()
        results = data.get("results")
        if not results:
            raise ValueError("No results found for this medication.")

        record = results[0]
        openfda = record.get("openfda", {})

        return {
            "name": openfda.get("generic_name", [drug_name])[0] if isinstance(openfda.get("generic_name"), list) else openfda.get("generic_name", drug_name),
            "manufacturer": openfda.get("manufacturer_name", ["Unknown"])[0] if isinstance(openfda.get("manufacturer_name"), list) else openfda.get("manufacturer_name", "Unknown"),
            "warnings": record.get("warnings", ["No warnings available"]),
            "purpose": record.get("purpose", ["Not specified"]),
        }

<?php
$keyword = isset($_GET['keyword']) ? $_GET['keyword'] : '';
$serviceName = "ProductAdvertisingAPI";
$region = "eu-west-1";
$accessKey = "your access key";
$secretKey = "your secret key";
$associateTag = "your associate tag";


class AwsV4 {
    private $accessKey = null;
    private $secretKey = null;
    private $path = null;
    private $regionName = null;
    private $serviceName = null;
    private $httpMethodName = null;
    private $queryParametes = array();
    private $awsHeaders = array();
    private $payload = "";

    private $HMACAlgorithm = "AWS4-HMAC-SHA256";
    private $aws4Request = "aws4_request";
    private $strSignedHeader = null;
    private $xAmzDate = null;
    private $currentDate = null;

    public function __construct($accessKey, $secretKey) {
        $this->accessKey = $accessKey;
        $this->secretKey = $secretKey;
        $this->xAmzDate = $this->getTimeStamp();
        $this->currentDate = $this->getDate();
    }

    function setPath($path) {
        $this->path = $path;
    }

    function setServiceName($serviceName) {
        $this->serviceName = $serviceName;
    }

    function setRegionName($regionName) {
        $this->regionName = $regionName;
    }

    function setPayload($payload) {
        $this->payload = $payload;
    }

    function setRequestMethod($method) {
        $this->httpMethodName = $method;
    }

    function addHeader($headerName, $headerValue) {
        $this->awsHeaders[$headerName] = $headerValue;
    }

    private function prepareCanonicalRequest() {
        $canonicalURL = "";
        $canonicalURL .= $this->httpMethodName . "\n";
        $canonicalURL .= $this->path . "\n" . "\n";
        $signedHeaders = '';
        foreach ($this->awsHeaders as $key => $value) {
            $signedHeaders .= $key . ";";
            $canonicalURL .= $key . ":" . $value . "\n";
        }
        $canonicalURL .= "\n";
        $this->strSignedHeader = substr($signedHeaders, 0, -1);
        $canonicalURL .= $this->strSignedHeader . "\n";
        $canonicalURL .= $this->generateHex($this->payload);
        return $canonicalURL;
    }

    private function prepareStringToSign($canonicalURL) {
        $stringToSign = '';
        $stringToSign .= $this->HMACAlgorithm . "\n";
        $stringToSign .= $this->xAmzDate . "\n";
        $stringToSign .= $this->currentDate . "/" . $this->regionName . "/" . $this->serviceName . "/" . $this->aws4Request . "\n";
        $stringToSign .= $this->generateHex($canonicalURL);
        return $stringToSign;
    }

    private function calculateSignature($stringToSign) {
        $signatureKey = $this->getSignatureKey($this->secretKey, $this->currentDate, $this->regionName, $this->serviceName);
        $signature = hash_hmac("sha256", $stringToSign, $signatureKey, true);
        $strHexSignature = strtolower(bin2hex($signature));
        return $strHexSignature;
    }

    public function getHeaders() {
        $this->awsHeaders['x-amz-date'] = $this->xAmzDate;
        ksort($this->awsHeaders);

        $canonicalURL = $this->prepareCanonicalRequest();

        $stringToSign = $this->prepareStringToSign($canonicalURL);

        $signature = $this->calculateSignature($stringToSign);

        if ($signature) {
            $this->awsHeaders['Authorization'] = $this->buildAuthorizationString($signature);
            return $this->awsHeaders;
        }
    }

    private function buildAuthorizationString($strSignature) {
        return $this->HMACAlgorithm . " " . "Credential=" . $this->accessKey . "/" . $this->getDate() . "/" . $this->regionName . "/" . $this->serviceName . "/" . $this->aws4Request . "," . "SignedHeaders=" . $this->strSignedHeader . "," . "Signature=" . $strSignature;
    }

    private function generateHex($data) {
        return strtolower(bin2hex(hash("sha256", $data, true)));
    }

    private function getSignatureKey($key, $date, $regionName, $serviceName) {
        $kSecret = "AWS4" . $key;
        $kDate = hash_hmac("sha256", $date, $kSecret, true);
        $kRegion = hash_hmac("sha256", $regionName, $kDate, true);
        $kService = hash_hmac("sha256", $serviceName, $kRegion, true);
        $kSigning = hash_hmac("sha256", $this->aws4Request, $kService, true);

        return $kSigning;
    }

    private function getTimeStamp() {
        return gmdate("Ymd\THis\Z");
    }

    private function getDate() {
        return gmdate("Ymd");
    }

    function setItemPage($itemPage) {
        $this->queryParametes['ItemPage'] = $itemPage;
    }
}

// Function to decode JSON safely
function safe_json_decode($json, $assoc = false) {
    $result = json_decode($json, $assoc);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('JSON decode error: ' . json_last_error_msg());
    }
    return $result;
}

// Initialize an empty array to hold all products
$all_products = [];
// Columns to save in CSV
$columns = ['asin', 'title', 'price', 'image_url', 'product_url', 'ASIN', 'BrowseNodeInfo.BrowseNodes.0.SalesRank', 'Offers.Listings.0.Price.Amount', 'Offers.Listings.0.Price.Currency', 'Offers.Listings.0.Price.DisplayAmount', 'Offers.Listings.0.SavingBasis.Percentage'];

// Loop over itemPage values from 1 to 5
for ($itemPage = 1; $itemPage <= 10; $itemPage++) {
    $payload = json_encode([
        "Keywords" => $keyword,
        "Resources" => [
            "BrowseNodeInfo.BrowseNodes.SalesRank",
            "BrowseNodeInfo.WebsiteSalesRank",
            "CustomerReviews.Count",
            "CustomerReviews.StarRating",
            "Images.Primary.Small",
            "Images.Primary.Medium",
            "Images.Primary.Large",
            "Images.Primary.HighRes",
            "Images.Variants.Small",
            "Images.Variants.Medium",
            "Images.Variants.Large",
            "Images.Variants.HighRes",
            "ItemInfo.ByLineInfo",
            "ItemInfo.ContentInfo",
            "ItemInfo.ContentRating",
            "ItemInfo.Classifications",
            "ItemInfo.ExternalIds",
            "ItemInfo.Features",
            "ItemInfo.ProductInfo",
            "ItemInfo.TechnicalInfo",
            "ItemInfo.Title",
            "Offers.Listings.Availability.Type",
            "Offers.Listings.DeliveryInfo.IsAmazonFulfilled",
            "Offers.Listings.DeliveryInfo.IsFreeShippingEligible",
            "Offers.Listings.DeliveryInfo.IsPrimeEligible",
            "Offers.Listings.DeliveryInfo.ShippingCharges",
            "Offers.Listings.LoyaltyPoints.Points",
            "Offers.Listings.Price",
            "Offers.Listings.ProgramEligibility.IsPrimeExclusive",
            "Offers.Listings.ProgramEligibility.IsPrimePantry",
            "Offers.Listings.Promotions",
            "Offers.Listings.SavingBasis",
            "Offers.Summaries.HighestPrice",
            "Offers.Summaries.LowestPrice",
            "Offers.Summaries.OfferCount",
            "ParentASIN",
            "SearchRefinements"
        ],
        "SearchIndex" => "Apparel",
        "ItemCount" => 100,
        "Availability" => "Available",
        "SortBy" => "Relevance",
        "ItemPage" => $itemPage,
        "PartnerTag" => $associateTag,
        "PartnerType" => "Associates",
        "Marketplace" => "www.amazon.in"
    ]);

    $host = "webservices.amazon.in";
    $uriPath = "/paapi5/searchitems";
    $awsv4 = new AwsV4($accessKey, $secretKey);
    $awsv4->setRegionName($region);
    $awsv4->setServiceName($serviceName);
    $awsv4->setPath($uriPath);
    $awsv4->setPayload($payload);
    $awsv4->setRequestMethod("POST");
    $awsv4->addHeader('content-encoding', 'amz-1.0');
    $awsv4->addHeader('content-type', 'application/json; charset=utf-8');
    $awsv4->addHeader('host', $host);
    $awsv4->addHeader('x-amz-target', 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems');
    $headers = $awsv4->getHeaders();
    $headerString = "";
    foreach ($headers as $key => $value) {
        $headerString .= $key . ': ' . $value . "\r\n";
    }

    $params = array(
        'http' => array(
            'header' => $headerString,
            'method' => 'POST',
            'content' => $payload
        )
    );
    $stream = stream_context_create($params);
    $fp = @fopen('https://' . $host . $uriPath, 'rb', false, $stream);

    if (!$fp) {
        throw new Exception("Exception Occurred");
    }
    $response = @stream_get_contents($fp);
    if ($response === false) {
        throw new Exception("Exception Occurred");
    }
    
    try {
        $response_array = safe_json_decode($response, true);
    } catch (Exception $e) {
        error_log($e->getMessage());
        continue; // Skip to the next itemPage if JSON decoding fails
    }

    if (isset($response_array['SearchResult']['Items'])) {
        foreach ($response_array['SearchResult']['Items'] as $item) {
            $asin = $item['ASIN'];
            $title = isset($item['ItemInfo']['Title']['DisplayValue']) ? $item['ItemInfo']['Title']['DisplayValue'] : 'N/A';
            $price = isset($item['Offers']['Listings'][0]['Price']['DisplayAmount']) ? $item['Offers']['Listings'][0]['Price']['DisplayAmount'] : 'N/A';
            $image_url = isset($item['Images']['Primary']['Large']['URL']) ? $item['Images']['Primary']['Large']['URL'] : 'placeholder.png';
            $product_url = isset($item['DetailPageURL']) ? $item['DetailPageURL'] : '#';

            $product = [
                'asin' => $asin,
                'title' => $title,
                'price' => $price,
                'image_url' => $image_url,
                'product_url' => $product_url,
                'ASIN' => $asin,
                'BrowseNodeInfo.BrowseNodes.0.SalesRank' => isset($item['BrowseNodeInfo']['BrowseNodes'][0]['SalesRank']) ? $item['BrowseNodeInfo']['BrowseNodes'][0]['SalesRank'] : 'N/A',
                'Offers.Listings.0.Price.Amount' => isset($item['Offers']['Listings'][0]['Price']['Amount']) ? $item['Offers']['Listings'][0]['Price']['Amount'] : 'N/A',
                'Offers.Listings.0.Price.Currency' => isset($item['Offers']['Listings'][0]['Price']['Currency']) ? $item['Offers']['Listings'][0]['Price']['Currency'] : 'N/A',
                'Offers.Listings.0.Price.DisplayAmount' => isset($item['Offers']['Listings'][0]['Price']['DisplayAmount']) ? $item['Offers']['Listings'][0]['Price']['DisplayAmount'] : 'N/A',
                'Offers.Listings.0.SavingBasis.Percentage' => isset($item['Offers']['Listings'][0]['SavingBasis']['Percentage']) ? $item['Offers']['Listings'][0]['SavingBasis']['Percentage'] : 'N/A'
            ];

            $all_products[] = $product;
        }
    }
}

// Save all products to a single CSV file
$csv_filename = 'productdataset.csv';
$csv_file = fopen($csv_filename, 'w');

// Write the headers
fputcsv($csv_file, $columns);

// Write the products
foreach ($all_products as $product) {
    $row = [];
    foreach ($columns as $col) {
        $row[] = isset($product[$col]) ? $product[$col] : '';
    }
    fputcsv($csv_file, $row);
}
fclose($csv_file);

// Return JSON response
header('Content-Type: application/json');
echo json_encode(['productdataset' => $all_products, 'csv_file_saved' => $csv_filename]);

?>

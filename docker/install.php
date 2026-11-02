<?php
// Generates configuration for the official 5.7 CLI installer. No application-table writes here.
require '/var/www/html/src/vendor/autoload.php';
use Symfony\Component\Yaml\Yaml;
function secret(string $key): string {
    $value = getenv($key);
    if ($value === false || $value === '') throw new RuntimeException("Missing $key");
    return $value;
}
$config = [
    'database' => [
        'hostName' => 'mysql', 'hostPort' => 3306, 'databaseName' => 'orangehrm',
        'privilegedDatabaseUser' => 'root', 'privilegedDatabasePassword' => secret('MYSQL_ROOT_PASSWORD'),
        'useSameDbUserForOrangeHRM' => 'n', 'orangehrmDatabaseUser' => 'orangehrm_app',
        'orangehrmDatabasePassword' => secret('MYSQL_PASSWORD'), 'isExistingDatabase' => 'n', 'enableDataEncryption' => 'n'
    ],
    'organization' => ['name' => 'Synthetic QA Laboratory', 'country' => 'US'],
    'admin' => [
        'adminUserName' => secret('ADMIN_USERNAME'), 'adminPassword' => secret('ADMIN_PASSWORD'),
        'adminEmployeeFirstName' => 'Synthetic', 'adminEmployeeLastName' => 'Administrator',
        'workEmail' => 'qa@example.invalid', 'contactNumber' => null, 'registrationConsent' => false
    ],
    'license' => ['agree' => 'y']
];
$path = '/var/www/html/installer/cli_install_config.yaml';
file_put_contents($path, Yaml::dump($config, 4)); chmod($path, 0600);
try {
    passthru('php /var/www/html/installer/cli_install.php', $status);
    if ($status !== 0 || !file_exists('/var/www/html/lib/confs/Conf.php')) throw new RuntimeException('Installer did not finish; inspect installer log');
} finally { unlink($path); }
// Restrict assertions to the exact columns used; PDO quotes secret literals safely.
$pdo = new PDO('mysql:host=mysql;port=3306', 'root', secret('MYSQL_ROOT_PASSWORD'), [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$password = $pdo->quote(secret('DB_PASSWORD'));
$pdo->exec("CREATE USER IF NOT EXISTS 'qa_reader'@'%' IDENTIFIED BY $password");
$pdo->exec("ALTER USER 'qa_reader'@'%' IDENTIFIED BY $password");
$pdo->exec("GRANT SELECT (emp_number, employee_id, emp_firstname, emp_middle_name, emp_lastname) ON orangehrm.hs_hr_employee TO 'qa_reader'@'%'");
echo "Read-only verification user ready.\n";

# pipe in master.passwd on FreeBSD, and get back commands that recreate the same entries using pw

BEGIN { FS = ":" }

{
	if ( $3 > 1000 && $3 != 65534 ) print "echo '" $2 "' | pw user add " $1 " -u " $3 " -c \"" $8 "\" -d " $9 " -s " $10 " -H 0"

}

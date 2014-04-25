# Accepts input in <from> <target>

BEGIN { 
    print "url.redirect = ("
    } 

{ 
    printf "\t\"^%s%\" => \"%s\",\n", $1, $2
}

END { 
    print ")" 
}

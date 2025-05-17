export function handlePopupCallback() {
    if (window.opener) {
        if (window.location.hash) {
            if (
                typeof window.opener.require === "function" &&
                window.opener.require("esri/kernel")
            ) {
                window.opener
                    .require("esri/kernel")
                    .id.setOAuthResponseHash(window.location.hash);
            } else {
                window.opener.dispatchEvent(
                    new CustomEvent("arcgis:auth:hash", {
                        detail: window.location.hash,
                    })
                );
            }
            window.close();
        } else if (window.location.search) {
            window.opener.dispatchEvent(
                new CustomEvent("arcgis:auth:location:search", {
                    detail: window.location.search,
                })
            );
            window.close();
        }
    } else {
        window.close();
    }
}
